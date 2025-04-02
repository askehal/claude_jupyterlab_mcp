from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.display import display, HTML
import os

# Import the MCP class
from claude_mcp import ClaudeMCP

@magics_class
class ClaudeMagics(Magics):
    def __init__(self, shell):
        super(ClaudeMagics, self).__init__(shell)
        # Initialize the MCP
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        try:
            self.mcp = ClaudeMCP(api_key=api_key)
            print("Claude MCP initialized successfully!")
        except Exception as e:
            print(f"Error initializing Claude MCP: {str(e)}")
    
    @cell_magic
    def claude(self, line, cell):
        """Send cell content to Claude and execute returned code"""
        print(f"Processing with line arguments: {line}")
        print(f"Cell content length: {len(cell)}")

        # Process arguments
        args = line.split()
        execute = True
        display_explanation = True
        show_code = True # Default to showing code
        model = "claude-3-5-sonnet-20240620"

        
        # Parse arguments
        for arg in args:
            if arg == "no-code":
                show_code = False
            elif arg == "no-exec":
                execute = False
            elif arg == "no-explain":
                display_explanation = False
            elif arg.startswith("model="):
                model = arg.split("=")[1]
        
        try:
            # Process with Claude
            result = self.mcp.query(
                cell, 
                model=model,
                execution=execute,
                display_explanation=display_explanation
            )
            # Show code if requested (requested by default)
            if show_code:
                print("Generated code:")
                print("```python")
                print(result["code"])
                print("```")
                print("\nOutput:")            
            
            # Return the output if execution was performed
            if execute and result.get("output"):
                return result["output"]
            else:
                return result["code"]
        except Exception as e:
            print(f"Error processing with Claude: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"
    
    @line_magic
    def claude_clear(self, line):
        """Clear Claude's conversation context"""
        try:
            return self.mcp.clear_context()
        except Exception as e:
            print(f"Error clearing context: {str(e)}")
            return f"Error: {str(e)}"
    
    @line_magic
    def claude_history(self, line):
        """Display execution history"""
        try:
            return self.mcp.get_history(format="html")
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return f"Error: {str(e)}"

# Function to load the extension
def load_ipython_extension(ipython):
    print("Loading Claude magic extension...")
    ipython.register_magics(ClaudeMagics)
    print("Claude magic extension loaded!")

def claude_last_code(self, line):
    """Display most recently generated code"""
    if not self.mcp.history:
        return "No code has been generated yet."
    
    last_result = self.mcp.history[-1]
    return f"Last generated code:\n```python\n{last_result['code']}\n```"