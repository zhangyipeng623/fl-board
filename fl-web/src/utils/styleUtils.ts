export const getTypeTagStyle = (type: string) => {
    const typeMap: Record<string, string> = {
        int: 'success',
        float: 'success',
        str: 'warning',
        datetime: 'danger',
        list: 'info',
        ndarray: 'info'
    }
    return typeMap[type.toLowerCase()] || 'info'
}