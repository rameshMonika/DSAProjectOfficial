def ascendingInsertionSort(arr,index):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key[index] < arr[j][index]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def descendingInsertionSort(arr,index):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key[index] > arr[j][index]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def ascendingQuickSort(arr,index):
    if len(arr) <= 10:
        return ascendingInsertionSort(arr)
    # pivot set to median distance
    pivot = arr[len(arr) // 2][index]
    # left contains all elements with distance less than pivot
    left = [x for x in arr if x[index] < pivot]
    middle = [x for x in arr if x[index] == pivot]
    # right contains all elements with distance greater than pivot
    right = [x for x in arr if x[index] > pivot]
    # recursively sort left and right
    return ascendingQuickSort(left,index) + middle + ascendingQuickSort(right,index)

def descendingQuickSort(arr,index):
    if len(arr) <= 10:
        return descendingInsertionSort(arr)
    # pivot set to median distance
    pivot = arr[len(arr) // 2][index]
    # left contains all elements with distance less than pivot
    left = [x for x in arr if x[index] < pivot]
    middle = [x for x in arr if x[index] == pivot]
    # right contains all elements with distance greater than pivot
    right = [x for x in arr if x[index] > pivot]
    # recursively sort left and right
    return descendingQuickSort(right,index) + middle + descendingQuickSort(left,index)

def sort_by_distance(data,order):
    if order == 'ascending':
        return ascendingQuickSort(data)
    elif order == 'descending':
        return descendingQuickSort(data)
    else:
        raise ValueError("Invalid order. Please enter 'ascending' or 'descending'.")