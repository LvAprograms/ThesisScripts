def find_x(node, high_res=False):
    x = 0
    if node == 1:
        return x
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
    node1 = node
    while node1 > 1:
        if node1 > nodes4:
            x += (node1 - nodes4) * dx1
            node1 -= (node1 - nodes4)
        elif nodes3 < node1 <= nodes4:
            x += (node1 - nodes3) * dx2
            node1 -= (node1 - nodes3)
        elif nodes2 < node1 <= nodes3:
            x += (node1 - nodes2) * dx3
            node1 -= (node1 - nodes2)
        elif nodes1 < node1 <= nodes2:
            x += (node1 - nodes1) * dx2
            node1 -= (node1 - nodes1)
        else:
            x += (node1-1) * dx1
            node1 -= node1
    # print(find_node(x))
    return x/1000

def find_node(x, high_res=False):
    dx1 = 10e3
    dx2 = 5e3
    dx3 = 1e3
    nodes1 = 90
    nodes2 = 110
    nodes3 = 910
    nodes4 = 930
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

if __name__ == "__main__":
    print(find_x(int(input("node: "))))
    # print(find_node(float(input("x: "))))