def find_x(node, high_res=False):
    x = 0
    dx1 = 10e3
    dx2 = 5e3
    dx3 = 2e3
    nodes1 = 90
    nodes2 = 110
    nodes3 = 460
    nodes4 = 480
    if high_res:
        dx3 = 400
        nodes3 = 1860
        nodes4 = 2000
    if node <= nodes1:
        x += node * dx1
    elif nodes1 < node <= nodes2:
        x += (node - nodes1)* dx2
    elif nodes2 < node <= nodes3:
        x += (node - nodes2) * dx3
    elif nodes3 < node <= nodes4:
        x += (node - nodes3) * dx2
    else:
        x += (node - nodes4) * dx1
    # print(find_node(x))
    return x/1000

def find_node(x, high_res=False):
    dx1 = 10e3
    dx2 = 5e3
    dx3 = 2e3
    nodes1 = 90
    nodes2 = 110
    nodes3 = 460
    nodes4 = 480
    if high_res:
        dx3 = 400
        nodes3 = 1860
        nodes4 = 2000

    m = x
    count = 0
    while m != 0:
        if count <= nodes1:
            m -= dx1
            count += 1
        elif nodes1 < count <= nodes2:
            m -= dx2
            count += 1
        elif nodes2 < count <= nodes3:
            m -= dx3
            count += 1
        elif nodes3 < count <= nodes4:
            m -= dx2
            count += 1
        else:
            m -= dx1
            count += 1
    return count