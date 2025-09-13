import json
import urllib.parse
import urllib.request

base = "http://localhost:8000"

# 1) get token (form-encoded)
data = urllib.parse.urlencode(
    {
        "grant_type": "password",
        "username": "test@example.com",
        "password": "password123",
        "scope": "",
        "client_id": "string",
        "client_secret": "string",
    }
).encode()
req = urllib.request.Request(base + "/api/v1/auth/token", data=data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
with urllib.request.urlopen(req) as resp:
    token_resp = resp.read().decode()
    print("token status", resp.getcode(), token_resp)
    token = json.loads(token_resp).get("access_token")

headers = {"Authorization": f"Bearer {token}"}


# helper to send JSON POST
def post_json(path, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        txt = resp.read().decode()
        print(path, resp.getcode(), txt)
        return json.loads(txt)


# 2) create post
post = post_json("/api/v1/posts/", {"title": "bench post", "content": "bench content"})
post_id = post.get("id")

# 3) create comment
_ = post_json("/api/v1/comments/", {"post_id": post_id, "content": "nice post!"})

# 4) create like
req = urllib.request.Request(
    base + f"/api/v1/likes/posts/{post_id}", data=b"", method="POST"
)
for k, v in headers.items():
    req.add_header(k, v)
with urllib.request.urlopen(req) as resp:
    txt = resp.read().decode()
    print("/likes create", resp.getcode(), txt)
