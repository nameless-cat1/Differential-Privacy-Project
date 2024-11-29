import math
import mysql.connector
import numpy as np


BETA = 1 / 10
EPSILON = 1
D = pow(10, 7) * 2
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

def get_query_result():

    query = (
        "SELECT s_suppkey, (l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity)/1000 AS num "
        "FROM supplier, partsupp, lineitem "
        "WHERE s_suppkey = l_suppkey AND ps_suppkey = l_suppkey AND ps_partkey = l_partkey "
        "ORDER BY num"
    )


    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='tpcd',
        auth_plugin='caching_sha2_password'
    )
    cursor = mydb.cursor()
    cursor.execute(query)
    result = np.array(cursor.fetchall())
    cursor.close()
    mydb.close()

    sorted_result = result[(-result[:, 1]).argsort()]
    u, t = np.hsplit(sorted_result, 2)
    return u.flatten(), t.flatten().astype(float)

def shift_inverse(f):
    s = np.full(D, -TAU - 1, dtype=int)
    for r in range(D):
        if f[TAU] == r:
            s[r] = 0
        else:
            j = binary_search(f, r)
            if 1 <= j <= TAU:
                s[r] = -TAU + j - 1
            elif TAU < j <= 2 * TAU:
                s[r] = TAU - j
    p = np.exp(EPSILON / 2 * s)
    p /= p.sum()
    r_tilde = np.random.choice(D, p=p)
    return r_tilde

def binary_search(f, r):
    low, high = 1, 2 * TAU
    while low <= high:
        mid = (low + high) // 2
        if f[mid] < r <= f[mid - 1]:
            return mid
        elif r <= f[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return -1

def count(t):
    aggregation_values = np.sort(t)
    _sum = np.sum(aggregation_values)
    f = [0] * (2 * TAU + 1)
    f[0] = _sum
    for j in range(1, 2 * TAU + 1):
        f[j] = _sum - np.sum(aggregation_values[-j:])
    return f

def get_evaluation_error(t, r_tilde):
    r = np.sum(t)
    relative_error = abs(r_tilde - r) / r
    print("The relative error: ", relative_error)
    return relative_error


user, tuple_counts = get_query_result()
print(user)
print(tuple_counts)

repeat_time = 5
relative_errors = []
f_k = count(tuple_counts)
print(np.sum(tuple_counts))

for i in range(repeat_time):
    r_tilde = shift_inverse(f_k)
    relative_errors.append(get_evaluation_error(tuple_counts, r_tilde))

print("The average relative error: ", np.average(relative_errors))