s = "/home/friedrich/lists/12_tech_brands.txt"
wl_name = s.lower()
# Remove .txt (4 chars)
wl_name = wl_name[:-4]
wl_name = wl_name.split("/")[-1]
print(wl_name)