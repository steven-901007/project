def intvalthe(function,number_one,number_two,accept_error):#中間值定理(intermediate value theorem)
    f = function #style = str 
    a = number_one #style = int or float
    b = number_two #style = int or float
    e = accept_error #style = float
    if type(f) != str:
        return TypeError("TypeError: function must be 'str'")
    try:
        f.index('=')
    except:
        return IndexError("IndexError: function must have a equal like '='")
    
    if type(a) != int and type(a) != float:
        return TypeError("TypeError: number_one must be 'int' or 'float'")
    
    if type(b) != int and type(b) != float:
        return TypeError("TypeError: number_two must be 'int' or 'float'")
    
    if type(e) != int and type(e) != float:
        return TypeError("TypeError: accept error must be 'int' or 'float'")
    
    f = f.replace("X",'x').replace("^","**").replace("=","-(")+")" #function 整理完成
    x = a 
    count_a = eval(f)

    x = b
    count_b = eval(f)
    if count_a == 0:
        return a
    elif count_b == 0:
        return b
    
    while abs(a-b) >= e:
        # print(a,b,abs(a-b))
        c = (a+b)/2
        x = c
        count_c = eval(f)
        if count_c*count_a <= 0:
            b = c
            x = b
            count_b = eval(f)
        else:
            a = c
            x = a
            count_a = eval(f)
    # return(a,b,abs(a-b))
    return a

print(intvalthe('(x^2-5)^0.5=3',3,4,0.000001))