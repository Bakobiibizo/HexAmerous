def tools_sql_table():
    """
    CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tools: LIST tool_id INTEGER NOT NULL,
    notes TEXT,  # Optional, can be NULL
    FOREIGN KEY (tool_id) REFERENCES tools (id)
    )
          
    """
    
def tool_sql_table():
    return """
    CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    command TEXT NOT NULL,
    api TEXT NOT NULL,
);"""