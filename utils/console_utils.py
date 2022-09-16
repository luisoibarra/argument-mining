import subprocess

def make_command(*args:str) -> str:
    """
    Build a command string based on the given `args`
    
    args: Parts of the command
    
    returns: The command's string representation
    """
    return " ".join(args)

def run_bash_command(command: str) -> None:
    """
    Run the `command` with bash
    
    command: Command to run
    """
    result = subprocess.run(["bash", "-c", command])