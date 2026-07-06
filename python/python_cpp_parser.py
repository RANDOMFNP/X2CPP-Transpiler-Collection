class ShrimpParser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.position = 0

    def peek(self) -> str | None:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def consume(self, expected: str = None) -> str:
        current = self.peek()
        if current is None:
            raise SyntaxError("Unexpected end of token stream")
        if expected and current != expected:
            raise SyntaxError(f"Expected '{expected}', got '{current}'")
        self.position += 1
        return current

    # Main function: Returns a top-level list of elements
    def parse(self) -> list:
        elements = []
        while self.peek() is not None:
            if self.peek() == "NEWLINE":
                self.consume("NEWLINE")
                continue
            elements.append(self.parse_element())
        return elements

    def parse_element(self) -> list:
        # Every element starts with a primary identifier name
        name = self.consume()
        
        # Start building the item's list with its identifier name
        element_structure = [name]

        # Scenario 1: Inline assignment ownership (name = value)
        if self.peek() == "=":
            self.consume("=")
            val_tokens = []
            while self.peek() and self.peek() != "NEWLINE":
                val_tokens.append(self.consume())
            
            # Append the right-side assignment value
            element_structure.append(" ".join(val_tokens))

        if self.peek() == "NEWLINE":
            self.consume("NEWLINE")

        # Scenario 2: Indentation block ownership
        if self.peek() == "INDENT":
            self.consume("INDENT")
            
            children = []
            while self.peek() and self.peek() != "DEDENT":
                if self.peek() == "NEWLINE":
                    self.consume("NEWLINE")
                    continue
                children.append(self.parse_element())
                
            self.consume("DEDENT")
            # Append the sub-list of children to show block ownership
            element_structure.append(children)

        return element_structure
