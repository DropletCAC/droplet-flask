from flask import Flask, request
from leak_detection import detect_leak
app = Flask(__name__)

@app.route('/', methods=['GET'])
def leak():
    if request.method == "GET":
        user, section, month, day = request.args.get('user'), request.args.get('section'), request.args.get('month'), request.args.get('day')
        print(user, section, month, day)
        is_leak = detect_leak(user, section, month=int(month), day=int(day))
        return str(is_leak)
    
if __name__ == "__main__":
    app.run()