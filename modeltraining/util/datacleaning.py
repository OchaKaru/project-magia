import re

def clean_data(text: str) -> str:
    input = text
    
    re.sub('\u00a0', ' ', input)
    
    input = input.encode("ascii", "ignore").decode()
    
    input = input.strip()
    re.sub(' {2,}', ' ', input)
    re.sub('\t{2,}', '\t', input)
    re.sub('\n{2,}', '\n', input)
    re.sub('\v{2,}', '\v', input)
    re.sub('\f{2,}', '\f', input)
    re.sub('\r{2,}', '\r', input)
    
    return input

    
    