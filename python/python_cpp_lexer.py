import re

# 1. Core token patterns (excluding indentation and newlines)
PATTERNS = [
    r'\d+(\.\d*)?',    # Numbers
    r'=',              # Assignment
    r'[A-Za-z_]\w*',   # Identifiers / Keywords
    r'[+\-*/]',        # Math operators
    r':',              # Colons (important for Python syntax block starts)
    r'==',
    r'>=',
    r'<=',
    r'>',
    r'<',
    r'!='
]

# 2. Structural patterns for line breaks and inline spacing
NEWLINE_PATTERN = re.compile(r'\n')
INLINE_WS_PATTERN = re.compile(r'[ \t]+')

def tokenize_python_style(code: str) -> list[str]:
    tokens = []
    position = 0
    length = len(code)
    
    compiled_patterns = [re.compile(p) for p in PATTERNS]
    
    # Indentation tracking stack (starts with 0 spaces/tabs base level)
    indent_stack = [0]
    
    # Set flag to check indentation at the absolute start of the string or after a newline
    is_line_start = True
    
    while position < length:
        # --- PHASE 1: Handle Line Starts & Indentation Levels ---
        if is_line_start:
            # Measure how much leading whitespace exists on this line
            ws_match = INLINE_WS_PATTERN.match(code, pos=position)
            indent_str = ws_match.group(0) if ws_match else ""
            indent_len = len(indent_str)
            
            # Advance cursor past the indentation whitespace
            if ws_match:
                position = ws_match.end()
                
            # Peek if the line is completely blank or just a comment line
            # If it is, we ignore indentation shifts for this line
            if position < length and (NEWLINE_PATTERN.match(code, pos=position) or code[position] == '#'):
                is_line_start = True
                if position < length and NEWLINE_PATTERN.match(code, pos=position):
                    position = NEWLINE_PATTERN.match(code, pos=position).end()
                continue
                
            current_indent = indent_stack[-1]
            
            if indent_len > current_indent:
                # Indentation increased -> New block starts
                indent_stack.append(indent_len)
                tokens.append("INDENT")
            elif indent_len < current_indent:
                # Indentation decreased -> Closing blocks
                while indent_len < indent_stack[-1]:
                    indent_stack.pop()
                    tokens.append("DEDENT")
                # Error check: Indent level must match an existing outer layer
                if indent_len != indent_stack[-1]:
                    raise IndentationError(f"Unindent does not match any outer indentation level")
                    
            is_line_start = False
            continue

        # --- PHASE 2: Handle Mid-Line Newlines ---
        nl_match = NEWLINE_PATTERN.match(code, pos=position)
        if nl_match:
            tokens.append("NEWLINE")
            position = nl_match.end()
            is_line_start = True # Next loop cycle must check indentation
            continue

        # --- PHASE 3: Handle Inline Spacing (Safe to skip between words) ---
        ws_match = INLINE_WS_PATTERN.match(code, pos=position)
        if ws_match:
            position = ws_match.end()
            continue

        # --- PHASE 4: Match Normal Language Tokens ---
        match_found = False
        for regex in compiled_patterns:
            match = regex.match(code, pos=position)
            if match:
                value = match.group(0)
                tokens.append(value)
                position = match.end()
                match_found = True
                break 
        
        if not match_found:
            raise SyntaxError(f"Unexpected character '{code[position]}' at index {position}")
            
    # --- PHASE 5: Clean up remaining open indent layers at EOF ---
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append("DEDENT")
        
    return tokens
