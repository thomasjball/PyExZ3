
l1 = [1, 2, 3]
l2 = [4, 5, 6]
print reduce(lambda x, y: x + y, [l1,l2,l1])