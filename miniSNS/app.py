from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
app.users = {}
app.posts = []
app.idCnt = 1

@app.route('/') 
def root():
    return """
    <h1>miniSNS</h1>
    <div>
        <button>메인 페이지</button>
        <button>회원 가입</button>
        <button>포스팅</button>
    </div>
    """

@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html', users=app.users)

@app.route('/sign-up', methods=['GET'])
def signUpPage():
    return render_template('signup.html')

@app.route('/sign-up', methods=['POST'])
def signup():
    newUser = request.json
    newUser['id'] = app.idCnt
    app.users[app.idCnt] = newUser
    app.idCnt += 1
    return jsonify(newUser)

@app.route('/post', methods=['POST'])
def post():
    payload = request.json
    userID = int(payload['id'])
    msg = payload['msg']

    if userID not in app.users:
        return '사용자가 존재하지 않습니다', 400
    if len(msg) > 300:
        return '300자를 초과했습니다', 400
    
    app.posts.append({
        'user_id' : userID,
        'post' : msg
    })
    return '성공', 200

@app.route('/follow', methods=['POST'])
def follow():
    payload = request.json
    userID = int(payload['id'])
    userIDToFollow = int(payload['follow'])

    if userID not in app.users or userIDToFollow not in app.users:
        return '사용자가 존재하지 않습니다.', 400
    
    user = app.users[userID]
    if user.get('follow'):
        user['follow'].append(userIDToFollow)
        user['follow'] = list(set(user['follow']))
    else:
        user['follow'] = [userIDToFollow]
        
    return jsonify(user)

@app.route('/unfollow', methods=['POST'])
def unfollow():
    payload = request.json
    userID = int(payload['id'])
    userIDToFollow = int(payload['unfollow'])

    if userID not in app.users or userIDToFollow not in app.users:
        return '사용자가 존재하지 않습니다.', 400
    
    user = app.users[userID]
    if user.get('follow'):
        try:    user['follow'].remove(userIDToFollow)
        except: pass
    else:
        user['follow'] = []
        
    return jsonify(user)

@app.route('/timeline/<int:userID>', methods=['GET'])
def timeline(userId):
    if userId not in app.users:
        return '사용자가 존재하지 않습니다', 400
    if app.users[userId].get('follow'):
        followList = set(app.users[userId]['follow'])
    else:
        followList = set()
    followList.add(userId)
    timeline= [msg for msg in app.posts if msg['userId'] in followList]

    return jsonify({
        'userId': userId,
        'timeline': timeline
    })

if __name__ == '__main__':
    app.run()