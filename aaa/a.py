import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def echo_function(text):
    """
    "A true echo is a single reflection of the sound source."

    Parameters
    ----------
    text: text to echo

    Returns
    -------
    text: return the input text parameter
    """

    print ("echooooooo: " + text)

    return text
