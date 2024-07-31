
# string = 'blahjksdfkj fdkasjf adsjfdie ak fidaofjpeofjjdkaj'
# chunk_size = 10
# overlap = 3


# for i in range(0, len(string), chunk_size-overlap):
#     print(string[i:i+chunk_size])


def func(**kwargs):
    kwargs['text'] = 'fjdfkjdfjad'
    return kwargs

print(func(pp=3, w=4))