import os
from anthropic import Anthropic
from IPython.display import display, HTML, Markdown
import json
import sys
from io import StringIO

class ClaudeMCP:
    """Model Context Protocol for integrating Claude with JupyterLab"""
    
    def __init__(self, api_key=None):
        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable or pass as parameter.")
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        
        # Maintain conversation context
        self.context = []
        
        # Track execution history
        self.history = []
    
    def query(self, prompt, model="claude-3-5-sonnet-20240620", execution=True, display_explanation=True):
        """Send a query to Claude and process the response"""
        # Add prompt to context
        self.context.append({"role": "user", "content": prompt})
        
        # Get response from Claude
        response = self.client.messages.create(
            model=model,
            max_tokens=4000, 
            messages=self.context
        )
        
        # Extract content from response
        content = response.content[0].text
        
        # Add response to context
        self.context.append({"role": "assistant", "content": content})
        
        # Extract code and explanation
        code = self._extract_code(content)
        explanation = self._extract_explanation(content, code)
        
        # Display explanation if requested
        if display_explanation and explanation:
            display(Markdown(explanation))
        
        # Execute code if requested
        if execution and code:
            output, error = self._execute_code(code)
            result = {"code": code, "output": output, "error": error, "explanation": explanation}
            self.history.append(result)
            
            # Display errors if any
            if error:
                print(f"Error: {error}")
            
            return result
        
        return {"code": code, "explanation": explanation}
    
    def _extract_code(self, response):
        """Extract Python code blocks from Claude's response"""
        code_blocks = []
        lines = response.split('\n')
        in_code_block = False
        current_block = []
        
        for line in lines:
            if line.strip() == "```python" or line.strip() == "```py":
                in_code_block = True
                continue
            elif line.strip() == "```" and in_code_block:
                in_code_block = False
                code_blocks.append('\n'.join(current_block))
                current_block = []
                continue
            
            if in_code_block:
                current_block.append(line)
        
        return '\n\n'.join(code_blocks)
    
    def _extract_explanation(self, response, code):
        """Extract Claude's explanation by removing code blocks"""
        explanation = response
        
        # Remove code blocks
        while "```python" in explanation or "```py" in explanation:
            start = explanation.find("```python") if "```python" in explanation else explanation.find("```py")
            start_marker_end = explanation.find("\n", start) + 1
            end = explanation.find("```", start_marker_end)
            end_marker_end = explanation.find("\n", end) + 1 if explanation.find("\n", end) != -1 else len(explanation)
            
            explanation = explanation[:start] + explanation[end_marker_end:]
        
        return explanation.strip()
    
    def _execute_code(self, code):
        """Execute Python code and capture output and errors"""
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        # Execute
        try:
            exec(code, globals())
            output = redirected_output.getvalue()
            error = None
        except Exception as e:
            output = redirected_output.getvalue()
            error = str(e)
        finally:
            sys.stdout = old_stdout
        
        return output, error
    
    def clear_context(self):
        """Clear the conversation context"""
        self.context = []
        return "Context cleared"
    
    def get_history(self, format="plain"):
        """Get execution history in specified format"""
        if format == "html":
            html = "<div style='font-family: Arial, sans-serif;'>"
            for i, item in enumerate(self.history):
                html += f"<div style='margin-bottom: 20px; border: 1px solid #eee; padding: 10px;'>"
                html += f"<h3>Execution {i+1}</h3>"
                html += f"<pre style='background-color: #f5f5f5; padding: 10px;'>{item['code']}</pre>"
                html += f"<h4>Output:</h4>"
                html += f"<pre style='background-color: #f9f9f9; padding: 10px;'>{item['output']}</pre>"
                if item['error']:
                    html += f"<h4>Error:</h4>"
                    html += f"<pre style='background-color: #fff0f0; padding: 10px;'>{item['error']}</pre>"
                html += "</div>"
            html += "</div>"
            return HTML(html)
        else:
            return self.history