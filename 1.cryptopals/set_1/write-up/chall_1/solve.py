# Convert hex to base64
import base64

pt = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
ct = base64.b64encode(bytes.fromhex(pt)).decode()
print(ct)