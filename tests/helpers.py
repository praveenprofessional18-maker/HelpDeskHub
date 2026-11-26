def login(client, email="alex@college.edu", password="correct-horse"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
