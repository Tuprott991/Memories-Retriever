"""
Fast BM25 Evaluation Script for Memories Retrieval Dataset
Evaluates BM25 retrieval performance using multiple metrics.
"""

import json
import time
from collections import defaultdict
from typing import List, Dict, Tuple
import numpy as np
from tqdm import tqdm


class SimpleBM25:
    """
    Fast BM25 implementation optimized for speed.
    Uses precomputed statistics and vectorized operations where possible.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_ids = []
        self.doc_freqs = {}
        self.idf = {}
        self.doc_len = []
        self.avgdl = 0
        self.N = 0
        
    def fit(self, corpus: List[str], doc_ids: List[str]):
        """Precompute all BM25 statistics."""
        self.corpus = corpus
        self.doc_ids = doc_ids
        self.N = len(corpus)
        
        # Tokenize and compute document lengths
        tokenized_corpus = []
        for doc in corpus:
            tokens = doc.lower().split()
            tokenized_corpus.append(tokens)
            self.doc_len.append(len(tokens))
        
        self.avgdl = sum(self.doc_len) / self.N if self.N > 0 else 0
        
        # Compute document frequencies
        for tokens in tokenized_corpus:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
        
        # Compute IDF scores
        for token, freq in self.doc_freqs.items():
            self.idf[token] = np.log((self.N - freq + 0.5) / (freq + 0.5) + 1.0)
        
        self.tokenized_corpus = tokenized_corpus
        
    def get_scores(self, query: str) -> np.ndarray:
        """Compute BM25 scores for all documents."""
        query_tokens = query.lower().split()
        scores = np.zeros(self.N)
        
        for token in query_tokens:
            if token not in self.idf:
                continue
                
            idf_score = self.idf[token]
            
            # Compute term frequency for each document
            for doc_idx, doc_tokens in enumerate(self.tokenized_corpus):
                tf = doc_tokens.count(token)
                if tf == 0:
                    continue
                    
                doc_length = self.doc_len[doc_idx]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avgdl))
                scores[doc_idx] += idf_score * (numerator / denominator)
        
        return scores
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search and return top-k documents."""
        scores = self.get_scores(query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include documents with non-zero scores
                results.append((self.doc_ids[idx], float(scores[idx])))
        
        return results


def calculate_metrics(rankings: List[str], relevant_id: str, k_values: List[int] = [1, 3, 5, 10]) -> Dict[str, float]:
    """
    Calculate retrieval metrics.
    
    Args:
        rankings: List of document IDs in ranked order
        relevant_id: The ID of the relevant document
        k_values: List of k values for metrics
    
    Returns:
        Dictionary of metrics
    """
    metrics = {}
    
    # Find position of relevant document (0-indexed)
    try:
        position = rankings.index(relevant_id)
        rank = position + 1  # 1-indexed rank
    except ValueError:
        position = -1
        rank = -1
    
    # Reciprocal Rank
    metrics['mrr'] = 1.0 / rank if rank > 0 else 0.0
    
    # Recall@K and Precision@K
    for k in k_values:
        if position >= 0 and position < k:
            metrics[f'recall@{k}'] = 1.0
            metrics[f'precision@{k}'] = 1.0 / k
        else:
            metrics[f'recall@{k}'] = 0.0
            metrics[f'precision@{k}'] = 0.0
    
    # MAP (for single relevant document, it's the same as precision at the rank)
    metrics['map'] = metrics['mrr']
    
    # NDCG@K
    for k in k_values:
        if position >= 0 and position < k:
            # For binary relevance with one relevant doc: NDCG = 1/log2(rank+1)
            metrics[f'ndcg@{k}'] = 1.0 / np.log2(position + 2)
        else:
            metrics[f'ndcg@{k}'] = 0.0
    
    return metrics


def evaluate_bm25(
    data_path: str = "data/queries.json",
    k1: float = 1.5,
    b: float = 0.75,
    top_k: int = 10,
    sample_size: int = None
) -> Dict:
    """
    Evaluate BM25 on the queries dataset.
    
    Args:
        data_path: Path to the queries JSON file
        k1: BM25 k1 parameter
        b: BM25 b parameter
        top_k: Number of top documents to retrieve
        sample_size: If set, only evaluate on a random sample
    
    Returns:
        Dictionary containing metrics and analysis
    """
    print(f"Loading data from {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} memories")
    
    # Sample if requested
    if sample_size and sample_size < len(data):
        import random
        random.seed(42)
        data = random.sample(data, sample_size)
        print(f"Sampled {sample_size} memories for evaluation")
    
    # Build corpus from captions
    corpus = [item['caption'] for item in data]
    doc_ids = [item['id'] for item in data]
    
    # Initialize and fit BM25
    print(f"Initializing BM25 (k1={k1}, b={b})...")
    start_time = time.time()
    bm25 = SimpleBM25(k1=k1, b=b)
    bm25.fit(corpus, doc_ids)
    index_time = time.time() - start_time
    print(f"Indexing completed in {index_time:.2f} seconds")
    
    # Evaluate on all queries
    all_metrics = defaultdict(list)
    query_count = 0
    failed_queries = []
    
    print("\nEvaluating queries...")
    start_time = time.time()
    
    for item in tqdm(data, desc="Processing memories"):
        memory_id = item['id']
        queries = item['queries']
        
        for query in queries:
            query_count += 1
            
            # Get rankings
            results = bm25.search(query, top_k=top_k)
            rankings = [doc_id for doc_id, score in results]
            
            # Calculate metrics
            metrics = calculate_metrics(rankings, memory_id)
            
            # Aggregate metrics
            for metric_name, value in metrics.items():
                all_metrics[metric_name].append(value)
            
            # Track failed queries (where relevant doc is not in top-k)
            if memory_id not in rankings:
                failed_queries.append({
                    'memory_id': memory_id,
                    'query': query,
                    'caption': item['caption'],
                    'top_results': results[:3]  # Show top 3
                })
    
    eval_time = time.time() - start_time
    print(f"Evaluation completed in {eval_time:.2f} seconds")
    print(f"Average time per query: {eval_time/query_count*1000:.2f} ms")
    
    # Compute average metrics
    avg_metrics = {}
    for metric_name, values in all_metrics.items():
        avg_metrics[metric_name] = np.mean(values)
    
    # Prepare results
    results = {
        'parameters': {
            'k1': k1,
            'b': b,
            'top_k': top_k,
            'num_memories': len(data),
            'num_queries': query_count
        },
        'timing': {
            'index_time': index_time,
            'eval_time': eval_time,
            'avg_query_time_ms': eval_time / query_count * 1000
        },
        'metrics': avg_metrics,
        'failed_queries_count': len(failed_queries),
        'failed_queries_sample': failed_queries[:10]  # Show first 10 failures
    }
    
    return results


def print_results(results: Dict):
    """Pretty print evaluation results."""
    print("\n" + "="*80)
    print("BM25 EVALUATION RESULTS")
    print("="*80)
    
    print("\nParameters:")
    for key, value in results['parameters'].items():
        print(f"  {key}: {value}")
    
    print("\nTiming:")
    for key, value in results['timing'].items():
        if 'time' in key.lower() and 'ms' not in key.lower():
            print(f"  {key}: {value:.2f} seconds")
        else:
            print(f"  {key}: {value:.2f}")
    
    print("\nMetrics:")
    metrics = results['metrics']
    
    # Group metrics by type
    print("\n  Ranking Metrics:")
    print(f"    MRR:  {metrics['mrr']:.4f}")
    print(f"    MAP:  {metrics['map']:.4f}")
    
    print("\n  Recall@K:")
    for k in [1, 3, 5, 10]:
        if f'recall@{k}' in metrics:
            print(f"    Recall@{k}:  {metrics[f'recall@{k}']:.4f}")
    
    print("\n  MRR@K:")
    print(f"    MRR@10:  {metrics['recall@10']:.4f}")
    
    print("\n  Precision@K:")
    for k in [1, 3, 5, 10]:
        if f'precision@{k}' in metrics:
            print(f"    Precision@{k}:  {metrics[f'precision@{k}']:.4f}")
    
    print("\n  NDCG@K:")
    for k in [1, 3, 5, 10]:
        if f'ndcg@{k}' in metrics:
            print(f"    NDCG@{k}:  {metrics[f'ndcg@{k}']:.4f}")
    
    print(f"\nFailed Queries: {results['failed_queries_count']} out of {results['parameters']['num_queries']}")
    
    if results['failed_queries_sample']:
        print("\nSample Failed Queries (first 3):")
        for i, failed in enumerate(results['failed_queries_sample'][:3], 1):
            print(f"\n  {i}. Memory ID: {failed['memory_id']}")
            print(f"     Query: {failed['query']}")
            print(f"     Caption: {failed['caption'][:100]}...")
            if failed['top_results']:
                print(f"     Top result: {failed['top_results'][0]}")
    
    print("\n" + "="*80)


def grid_search(data_path: str = "data/queries.json", sample_size: int = 100):
    """
    Perform grid search over BM25 parameters.
    
    Args:
        data_path: Path to the queries JSON file
        sample_size: Number of memories to use for grid search
    """
    k1_values = [0.5, 1.0, 1.5, 2.0]
    b_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    print(f"\nGrid Search: Testing {len(k1_values)} k1 values × {len(b_values)} b values")
    print("="*80)
    
    best_mrr = 0
    best_params = None
    all_results = []
    
    for k1 in k1_values:
        for b in b_values:
            print(f"\nTesting k1={k1}, b={b}...")
            results = evaluate_bm25(data_path, k1=k1, b=b, sample_size=sample_size)
            mrr = results['metrics']['mrr']
            
            all_results.append({
                'k1': k1,
                'b': b,
                'mrr': mrr,
                'recall@10': results['metrics']['recall@10']
            })
            
            print(f"  MRR: {mrr:.4f}, Recall@10: {results['metrics']['recall@10']:.4f}")
            
            if mrr > best_mrr:
                best_mrr = mrr
                best_params = (k1, b)
    
    print("\n" + "="*80)
    print("GRID SEARCH RESULTS")
    print("="*80)
    print(f"\nBest Parameters: k1={best_params[0]}, b={best_params[1]}")
    print(f"Best MRR: {best_mrr:.4f}")
    
    print("\nAll Results:")
    print(f"{'k1':<6} {'b':<6} {'MRR':<10} {'Recall@10':<10}")
    print("-" * 40)
    for res in sorted(all_results, key=lambda x: x['mrr'], reverse=True):
        print(f"{res['k1']:<6.1f} {res['b']:<6.2f} {res['mrr']:<10.4f} {res['recall@10']:<10.4f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate BM25 on memories dataset")
    parser.add_argument('--data-path', type=str, default='data/queries.json',
                        help='Path to queries JSON file')
    parser.add_argument('--k1', type=float, default=1.5,
                        help='BM25 k1 parameter')
    parser.add_argument('--b', type=float, default=0.75,
                        help='BM25 b parameter')
    parser.add_argument('--top-k', type=int, default=10,
                        help='Number of top documents to retrieve')
    parser.add_argument('--sample-size', type=int, default=None,
                        help='Sample size for evaluation (for quick testing)')
    parser.add_argument('--grid-search', action='store_true',
                        help='Perform grid search over parameters')
    parser.add_argument('--grid-sample', type=int, default=100,
                        help='Sample size for grid search')
    parser.add_argument('--output', type=str, default=None,
                        help='Save results to JSON file')
    
    args = parser.parse_args()
    
    if args.grid_search:
        grid_search(args.data_path, sample_size=args.grid_sample)
    else:
        results = evaluate_bm25(
            data_path=args.data_path,
            k1=args.k1,
            b=args.b,
            top_k=args.top_k,
            sample_size=args.sample_size
        )
        
        print_results(results)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")
