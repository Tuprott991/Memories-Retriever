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
      id: "home-1",
      type: "photo",
      title: "THE FRONT PORCH IN SPRING",
      description: "Remember your beautiful front porch in the springtime? You loved sitting there in the morning with your coffee, watching the neighborhood come to life. The flowers you planted yourself were always blooming so beautifully - those pink azaleas and white dogwoods. You'd wave to everyone passing by, and they'd stop to chat. That porch was where so many conversations happened, where grandchildren learned to ride their bikes up and down the walkway.",
      mediaUrl: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=80",
      timestamp: "Spring 1982"
    },
    {
      id: "home-2",
      type: "video",
      title: "CHRISTMAS MORNING IN THE LIVING ROOM",
      description: "This is Christmas morning 1985 in your living room! Look at that beautiful tree you decorated, reaching almost to the ceiling. The children are running down the stairs in their pajamas, so excited they could barely sleep. You're standing by the fireplace in your red sweater, the one you wore every Christmas. The stockings are hung, the presents are piled high, and everyone's laughter fills the whole house.",
      mediaUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
      timestamp: "December 25, 1985"
    },
    {
      id: "home-3",
      type: "photo",
      title: "THE KITCHEN WHERE MAGIC HAPPENED",
      description: "Your kitchen - the heart of your home! This is where you baked all those pies, prepared Sunday dinners for the whole family. That yellow checkered tablecloth was always there, and the smell of fresh bread would fill the entire house. The grandchildren would sit at that table doing homework while you cooked, and you'd help them with their math problems between stirring pots. Every holiday meal started here, with you at the center of it all.",
      mediaUrl: "https://images.unsplash.com/photo-1556912167-f556f1f39faa?w=1200&q=80",
      timestamp: "1978"
    },
    {
      id: "home-4",
      type: "photo",
      title: "THE BACKYARD GARDEN",
      description: "Your pride and joy - the backyard garden you tended for over thirty years! Those tomato plants, the rows of green beans, the herbs by the fence. You knew every plant by name, when to water them, when to harvest. The grandchildren would help you pick vegetables in the summer, and you'd teach them which ones were ready. That old wooden bench under the oak tree was where you'd rest and admire your work.",
      mediaUrl: "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&q=80",
      timestamp: "Summer 1983"
    },
    {
      id: "home-5",
      type: "video",
      title: "THANKSGIVING DINNER PREPARATION",
      description: "Here's the whole family helping you prepare Thanksgiving dinner! The kitchen is bustling with activity - daughters peeling potatoes, grandchildren setting the table, everyone pitching in. You're checking the turkey in the oven, making sure everything is perfect. The house smells amazing, and there's so much love and laughter. This was what you loved most - having everyone together under one roof.",
      mediaUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
      timestamp: "November 1987"
    },
    {
      id: "home-6",
      type: "photo",
      title: "THE MASTER BEDROOM",
      description: "Your peaceful sanctuary - the master bedroom where you and Grandpa shared so many quiet moments. That handmade quilt on the bed was a wedding gift, and you kept it for over forty years. The photos on the dresser told your family's story - wedding day, children's births, graduations. Every morning you'd open those curtains and let the sunlight in, starting another day in the home you loved.",
      mediaUrl: "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=1200&q=80",
      timestamp: "1980"
    },
    {
      id: "home-7",
      type: "photo",
      title: "THE DINING ROOM TABLE",
      description: "This dining room table saw it all! Birthday parties, holiday feasts, family meetings, homework sessions. You could fit twelve people around it when you added the extra leaves. The chandelier above was one of your first purchases for the house. Every Sunday after church, the family would gather here for your pot roast dinner. The laughter, the stories, the love shared around this table - it held your family together.",
      mediaUrl: "https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?w=1200&q=80",
      timestamp: "1975"
    },
    {
      id: "home-8",
      type: "video",
      title: "SUMMER EVENING ON THE BACK DECK",
      description: "A beautiful summer evening on the deck Grandpa built! You're all sitting outside, enjoying the sunset, sipping lemonade. The kids are playing in the yard, catching fireflies. You and Grandpa are in your favorite chairs, just watching and smiling. These quiet evenings were some of your favorites - no special occasion needed, just family being together, enjoying the home you built.",
      mediaUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
      timestamp: "July 1986"
    },
    {
      id: "home-9",
      type: "photo",
      title: "THE CHILDREN'S PLAYROOM",
      description: "Remember when you converted the spare room into a playroom for the grandchildren? Toys everywhere, books on the shelves, that little table where they'd color and do crafts. You kept a box of dress-up clothes and art supplies. On rainy days, this room was filled with imagination and creativity. You'd sit in the corner reading to them, or helping with a puzzle. They knew this room was their special place at Grandma's house.",
      mediaUrl: "https://images.unsplash.com/photo-1631947430066-48c30d57b943?w=1200&q=80",
      timestamp: "1988"
    },
    {
      id: "home-10",
      type: "photo",
      title: "THE DRIVEWAY - COMINGS AND GOINGS",
      description: "Your driveway - where every visit began and ended. You'd stand right there at the door, waving goodbye to everyone after Sunday dinner, watching until their cars disappeared around the corner. And you'd be there waiting when they arrived, ready with hugs. That driveway saw first cars, taught teenagers to drive, welcomed new babies home. It was the threshold between the world and the warmth of your home.",
      mediaUrl: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&q=80",
      timestamp: "1984"
    },
    {
      id: "home-11",
      type: "video",
      title: "BIRTHDAY PARTY IN THE LIVING ROOM",
      description: "What a celebration! Someone's birthday party in your living room - balloons, streamers, cake and ice cream! All the grandchildren are here, singing happy birthday at the top of their lungs. You're bringing out the cake with candles blazing, everyone's faces glowing with excitement. Your home was the gathering place for every birthday, every celebration. You made sure no one ever felt forgotten on their special day.",
      mediaUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
      timestamp: "March 1986"
    },
    {
      id: "home-12",
      type: "photo",
      title: "THE FRONT DOOR - WELCOME HOME",
      description: "Your welcoming front door - painted that cheerful blue color you loved. The wreath changed with the seasons - flowers in spring, harvest in fall, evergreen in winter. That doorbell rang thousands of times, and you always answered with a smile. Behind this door was love, warmth, delicious food, and unconditional acceptance. Everyone knew that walking through this door meant coming home.",
      mediaUrl: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=80",
      timestamp: "1981"
    }
  ]
};
