import { NextResponse } from 'next/server';
import { LeaderboardEntry } from '@/lib/types';

const NOTION_DATABASE_ID = '2680cdbf-4977-8119-89fc-fba3dd92f096'; // Thunder Quiz Leaderboard database with proper formatting

export async function GET() {
  try {
    if (!process.env.NOTION_API_KEY) {
      console.error('NOTION_API_KEY not configured');
      return NextResponse.json({ scores: [], entries: [] });
    }

    // Query Notion database using direct API call
    const response = await fetch(`https://api.notion.com/v1/databases/${NOTION_DATABASE_ID}/query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.NOTION_API_KEY}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        page_size: 10,
        sorts: [
          {
            property: 'Score',
            direction: 'descending'
          }
        ]
      })
    });

    if (!response.ok) {
      throw new Error(`Notion API error: ${response.status}`);
    }

    const data = await response.json();

    const entries: LeaderboardEntry[] = data.results.map((page: any) => ({
      id: page.id,
      nickname: page.properties.Player?.title?.[0]?.text?.content || 'Unknown',
      score: page.properties.Score?.number || 0,
      playerGoals: page.properties.Score?.number || 0,
      opponentGoals: page.properties['Opponent Score']?.number || 0,
      accuracy: page.properties.Accuracy?.number || 0,
      date: page.properties.Date?.date?.start || page.created_time || new Date().toISOString(),
    }));

    return NextResponse.json({ 
      scores: entries,
      entries: entries 
    });
  } catch (error) {
    console.error('Error fetching leaderboard from Notion:', error);
    // Return empty leaderboard on error
    return NextResponse.json({ scores: [], entries: [] });
  }
}

export async function POST(request: Request) {
  try {
    const entry: LeaderboardEntry = await request.json();
    
    if (!process.env.NOTION_API_KEY) {
      console.error('NOTION_API_KEY not configured');
      return NextResponse.json(
        { error: 'Notion not configured' },
        { status: 500 }
      );
    }
    
    // Calculate goal differential
    const goalDiff = entry.playerGoals - entry.opponentGoals;
    
    // Determine result
    let result = '📊 Tie';
    if (goalDiff > 0) result = '🏆 Win';
    else if (goalDiff < 0) result = '💪 Loss';
    
    // Create page in Notion database using direct API call
    const response = await fetch('https://api.notion.com/v1/pages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.NOTION_API_KEY}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        parent: { database_id: NOTION_DATABASE_ID },
        properties: {
          Player: {  // Title property
            title: [
              {
                text: {
                  content: entry.nickname || 'Anonymous',
                },
              },
            ],
          },
          Score: {
            number: entry.playerGoals || 0,
          },
          'Opponent Score': {
            number: entry.opponentGoals || 0,
          },
          'Goal Diff': {
            number: goalDiff,
          },
          Accuracy: {
            number: (entry.accuracy || 0) / 100, // Convert to decimal for percent field
          },
          Date: {
            date: {
              start: new Date().toISOString(),
            },
          },
          Result: {
            select: {
              name: result,
            },
          },
        },
      })
    });
    
    if (!response.ok) {
      throw new Error(`Notion API error: ${response.status}`);
    }
    
    const pageData = await response.json();
    
    return NextResponse.json({ 
      success: true, 
      entry: {
        ...entry,
        id: pageData.id,
        date: new Date(),
      },
      rank: 0  // We'll calculate rank separately if needed
    });
  } catch (error) {
    console.error('Error saving to Notion leaderboard:', error);
    return NextResponse.json(
      { error: 'Failed to save score to Notion' },
      { status: 500 }
    );
  }
}