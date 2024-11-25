import math

import mysql.connector
import numpy as np


def get_query_result():
    # Q18
    # query = (
    #     "select c_custkey, l_quantity "
    #     "from customer, orders, lineitem "
    #     "where c_custkey = o_custkey "
    #     "and l_orderkey = o_orderkey "
    #     "order by l_quantity"
    # )

    # Q9
    query = (
        "select s_suppkey, (l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity)/1000 as num "
        "from supplier, partsupp, lineitem "
        "where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey "
        "order by num"
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
    sorted_result = result[(-result[:, 1]).argsort()]
    u, t = np.hsplit(sorted_result, 2)
    u = u.flatten()
    t = t.flatten().astype(float)
    return u, t



def shift_inverse(f):
    s = [-TAU - 1] * D
    for r in range(D):
        if r == f[TAU]:
            s[r] = 0
        else:
            j = binary_search(f, r)
            if j != -1:
                if TAU < j <= 2 * TAU:
                    s[r] = TAU - j
                elif 1 <= j <= TAU:
                    s[r] = -TAU + j - 1
    p = np.array([np.exp(EPSILON / 2 * s[r]) for r in range(D)])
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
    aggregation_values=sorted(t)
    _sum=np.sum(aggregation_values)
    f = [0] * (2 * TAU+1)
    f[0]=_sum
    for j in range(1, 2 * TAU + 1):
        f[j] = _sum-sum(aggregation_values[-j:])
    return f

def get_evaluation_error(t, r_tilde):
    r = np.sum(t)
    relative_error = abs(r_tilde - r) / r
    print("The relative_error: ", relative_error)
    return relative_error

BETA = 1 / 10
EPSILON = 1
D = pow(10, 7)*2
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

user, tuple = get_query_result()

print(user)
print(tuple)

repeat_time=5
relative_errors=[]
f_k = count(tuple)
print(np.sum(tuple))

for i in range(repeat_time):
    r_tilde = shift_inverse(f_k)
    print("r_tilde ",r_tilde)
    relative_errors.append(get_evaluation_error(tuple, r_tilde))

print("The average relative_error: ", np.average(relative_errors))
