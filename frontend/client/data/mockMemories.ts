export interface MockMemoryData {
  query: string;
  paraphrasedQuery: string;
  reasoning: string;
  memories: Array<{
    id: string;
    type: "photo" | "video";
    title: string;
    description: string;
    mediaUrl: string;
    timestamp: string;
  }>;
}

export const ourHomeMockData: MockMemoryData = {
  query: "Tell me about our home",
  paraphrasedQuery: "Retrieving memories about your beloved home, the place where your family gathered, celebrated, and created countless precious moments together...",
  reasoning: "Analyzing memory graph... Found connections between home, family gatherings, holidays, daily routines, and special celebrations. Retrieving most significant memories...",
  memories: [
    {
      id: "memory-1",
      type: "video",
      title: "COOKING CAKES WITH GRANDDAUGHTER",
      description: "What a beautiful moment! This video shows you cooking with your granddaughter at home, baking delicious cakes together. The kitchen is filled with flour, sugar, and so much love. You're teaching her all your secret recipes, the ones passed down through generations. She's watching you carefully, learning not just how to bake, but the joy of creating something special with family. The laughter, the mess, the memories - this is what it's all about.",
      mediaUrl: "/vid_1.mp4",
      timestamp: "2023"
    },
    {
      id: "memory-2",
      type: "video",
      title: "DAUGHTER'S GRADUATION CEREMONY",
      description: "A proud moment captured forever! This is your daughter's graduation ceremony, and the joy is overwhelming. Balloons are everywhere, celebrating this incredible achievement. You're beaming with pride as she walks across that stage, diploma in hand. All those years of hard work, late-night studying, and determination have led to this moment. The ceremony is beautiful, surrounded by family and friends who came to celebrate. This is a day you'll never forget - watching your daughter reach for her dreams.",
      mediaUrl: "/vid_2.mp4",
      timestamp: "2024"
    },
    {
      id: "memory-3",
      type: "photo",
      title: "FAMILY DAY AT THE BEACH",
      description: "A perfect family day at the beach! The sun is shining, the waves are gentle, and everyone is together. This photo captures your whole family enjoying the sand and sea - building sandcastles, splashing in the water, collecting seashells. These are the simple moments that mean everything: kids running freely, parents relaxing, grandparents watching with joy. The beach has always been your special place to reconnect, to laugh, and to make memories that will last forever.",
      mediaUrl: "/image_3.png",
      timestamp: "2022"
    },
    {
      id: "memory-4",
      type: "video",
      title: "WEDDING DAY WITH JOHN",
      description: "Your wedding day with John - the beginning of your beautiful journey together! This video displays the most romantic day of your life, filled with love, promises, and hope for the future. You look radiant, John looks handsome, and everyone around you is celebrating your union. The vows, the first dance, the tears of joy - every moment is precious. This is where your story began, the foundation of the family you built together, the love that has lasted through the years.",
      mediaUrl: "/vid_4.mp4",
      timestamp: "1995"
    },
    {
      id: "memory-5",
      type: "photo",
      title: "YOUR FIRST CHILD",
      description: "The moment everything changed - your first child! This precious photo captures the tiny miracle that made you a parent for the very first time. Those tiny fingers, that sweet face, the overwhelming love you felt the instant you held them. This was the beginning of your journey as a mother, the start of all the adventures, challenges, and joys that parenthood would bring. Looking at this photo brings back all those feelings - the wonder, the responsibility, the pure, unconditional love.",
      mediaUrl: "/image_5.png",
      timestamp: "1996"
    }
  ]
};
