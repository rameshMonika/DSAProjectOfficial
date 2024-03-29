def insertionSort(arr):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key[1] < arr[j][1]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def ascendingQuickSort(arr):
    if len(arr) <= 10:
        return insertionSort(arr)
    # pivot set to median distance
    pivot = arr[len(arr) // 2][1]
    # left contains all elements with distance less than pivot
    left = [x for x in arr if x[1] < pivot]
    middle = [x for x in arr if x[1] == pivot]
    # right contains all elements with distance greater than pivot
    right = [x for x in arr if x[1] > pivot]
    # recursively sort left and right
    return ascendingQuickSort(left) + middle + ascendingQuickSort(right)

def descendingQuickSort(arr):
    if len(arr) <= 10:
        return insertionSort(arr)
    # pivot set to median distance
    pivot = arr[len(arr) // 2][1]
    # left contains all elements with distance less than pivot
    left = [x for x in arr if x[1] < pivot]
    middle = [x for x in arr if x[1] == pivot]
    # right contains all elements with distance greater than pivot
    right = [x for x in arr if x[1] > pivot]
    # recursively sort left and right
    return descendingQuickSort(right) + middle + descendingQuickSort(left)

def sort_by_distance(data,order):
    if order == 'ascending':
        return ascendingQuickSort(data)
    elif order == 'descending':
        return descendingQuickSort(data)
    else:
        raise ValueError("Invalid order. Please enter 'ascending' or 'descending'.")