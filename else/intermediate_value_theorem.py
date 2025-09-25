def intvalthe(function,number_one,number_two,accept_error):#中間值定理(intermediate value theorem)
    f = function #style = str 
    if number_one == number_two:
        return ValueError("ValueError: number one can't equal to number two")
    elif number_one > number_two:
        b = number_one
        a = number_two
    else:
        a = number_one #style = int or float
        b = number_two #style = int or float
    e = accept_error #style = float
    if type(f) != str:
        return TypeError("TypeError: function must be 'str'")
    try:
        f.index('=')
    except:
        return IndexError("IndexError: function must have a equal like '='")

    f = f.replace("X",'x').replace("^","**").replace("=","-(")+")" #function 整理完成

    if type(a) != int and type(a) != float:
        return TypeError("TypeError: number_one must be 'int' or 'float'")
    
    x = a 
    count_a = eval(f)

    if type(b) != int and type(b) != float:
        return TypeError("TypeError: number_two must be 'int' or 'float'")

    x = b
    count_b = eval(f)
    touch_text = 0
    if count_b*count_a>0:
        for i in range(a,b):
            x = i
            count_x = eval(f)
            if count_b*count_x < 0 or count_a*count_x < 0:
                touch_text+=1
    if touch_text == 0:
        return IndexError("IndexError: can't find any x for f(x)~=0 between geven number(or get two x that f(x)~=0 but both x have same int)")
    
    if type(e) != int and type(e) != float:
        return TypeError("TypeError: accept error must be 'int' or 'float'")
  
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