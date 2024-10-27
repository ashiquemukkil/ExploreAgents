
def insertionSort2(n, arr):
    print(*arr)
    for i in range(1,n):
        key =arr[i]
        j = i-1
        while j>=0 and arr[j]>key:
            arr[j+1] = arr[j]
            j-=1
        arr[j+1] = key
        print(*arr)

def quicksort(arr):
    if len(arr)<=1:
        return arr
    pivot = arr[int(len(arr)//2)]
    left = [i for i in arr if i<pivot]
    middle = [i for i in arr if i==pivot]
    right = [i for i in arr if i>pivot]
    return quicksort(left)+middle+quicksort(right)

def radio(i,k):
    s_k = sorted(k, key=lambda y: int(y))
    j = 0
    for index,i in enumerate(s_k):
        
    # for i in range(i,len(k),i*2):
    #     j+=1
    

# _1_3_5_7_9_
if __name__ == "__main__":
    print(radio(1,[1,2,3,4,5,6,7,8,9,10]))