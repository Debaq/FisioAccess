def fx(actual_number, step):
    factor = 1.2
    number = actual_number
    if step > 0:
        for i in range(step):
            number = number*factor
    elif step == 0:
        return number
    elif step < 0:
        for i in range(abs(step)):
            number = number/factor
    
    return round(number)
            
print(fx(186, -4))
