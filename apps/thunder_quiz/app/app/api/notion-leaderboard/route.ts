import { NextResponse } from 'next/server';

const NOTION_API_KEY = process.env.NOTION_API_KEY;
const NOTION_DATABASE_ID = '2680cdbf-4977-8119-89fc-fba3dd92f096';

const notionHeaders = {
  'Authorization': `Bearer ${NOTION_API_KEY}`,
  'Content-Type': 'application/json',
  'Notion-Version': '2022-06-28',
};

export async function GET() {
  try {
    // Query the Notion database for leaderboard entries
    const response = await fetch(`https://api.notion.com/v1/databases/${NOTION_DATABASE_ID}/query`, {
      method: 'POST',
      headers: notionHeaders,
      body: JSON.stringify({
        sorts: [
          {
            property: 'Goal Diff',
            direction: 'descending'
          },
          {
            property: 'Score',
            direction: 'descending'
          }
        ],
        page_size: 10
      })
    });

    if (!response.ok) {
      throw new Error(`Notion API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Transform Notion data to our leaderboard format
    const scores = data.results.map((page: any) => ({
      id: page.id,
      nickname: page.properties.Player?.title?.[0]?.plain_text || 'Unknown',
      playerGoals: page.properties.Score?.number || 0,
      opponentGoals: page.properties['Opponent Score']?.number || 0,
      accuracy: Math.round((page.properties.Accuracy?.number || 0) * 100),
      date: page.properties.Date?.date?.start || new Date().toISOString(),
    }));

    return NextResponse.json({ scores });
  } catch (error) {
    console.error('Error fetching Notion leaderboard:', error);
    // Fallback to empty leaderboard
    return NextResponse.json({ scores: [] });
  }
}

export async function POST(request: Request) {
  try {
    const entry = await request.json();
    
    // Determine result based on scores
    let result = '📊 Tie';
    if (entry.playerGoals > entry.opponentGoals) {
      result = '🏆 Win';
    } else if (entry.playerGoals < entry.opponentGoals) {
      result = '💪 Loss';
    }
    
    // Create a new page in the Notion database
    const response = await fetch('https://api.notion.com/v1/pages', {
      method: 'POST',
      headers: notionHeaders,
      body: JSON.stringify({
        parent: { database_id: NOTION_DATABASE_ID },
        properties: {
          'Player': {
            title: [
              {
                text: {
                  content: entry.nickname || 'Anonymous'
                }
              }
            ]
          },
          'Score': {
            number: entry.playerGoals
          },
          'Opponent Score': {
            number: entry.opponentGoals
          },
          'Accuracy': {
            number: (entry.accuracy || 0) / 100
          },
          'Date': {
            date: {
              start: new Date().toISOString().split('T')[0]
            }
          },
          'Result': {
            select: {
              name: result
            }
          },
          'Goal Diff': {
            number: entry.playerGoals - entry.opponentGoals
          }
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Notion API error:', errorData);
      throw new Error(`Notion API error: ${response.status}`);
    }

    const createdPage = await response.json();
    
    return NextResponse.json({ 
      success: true, 
      entry: {
        ...entry,
        id: createdPage.id
      }
    });
  } catch (error) {
    console.error('Error saving to Notion leaderboard:', error);
    return NextResponse.json(
      { error: 'Failed to save score' },
      { status: 500 }
    );
  }
}