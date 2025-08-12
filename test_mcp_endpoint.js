const endpoint = 'http://localhost:3003/api/mcp';

// Test with just Content-Type
fetch(endpoint, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tool: 'search_hockey_rules',
    parameters: { query: 'offside' }
  })
})
.then(r => console.log('Without Accept:', r.status, r.statusText))
.catch(e => console.error('Error without Accept:', e));

// Test with Accept header
fetch(endpoint, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    tool: 'search_hockey_rules',
    parameters: { query: 'offside' }
  })
})
.then(r => console.log('With Accept:', r.status, r.statusText))
.catch(e => console.error('Error with Accept:', e));
