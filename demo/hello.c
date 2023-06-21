void main() {
    int* led = (int*)0xffff0000;
    while (1) {
        int n = 2400;
        while (n--);
        *led += 1;
    }
}
