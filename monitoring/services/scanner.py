def calculate_score(keyword, content):
    kw = keyword.name.lower()
    title = content.title.lower()
    body = content.body.lower()

    if kw == title:
        return 100
    elif kw in title:
        return 70
    elif kw in body:
        return 40
    return 0