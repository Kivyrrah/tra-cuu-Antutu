import time
import requests
import cloudscraper
from bs4 import BeautifulSoup
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu
from tkinter import ttk

def info_finder(url, soc_ver):
    scraper = cloudscraper.create_scraper()  # giống requests nhưng bypass cloudflare

    try:
        r = scraper.get(url)
        r.raise_for_status()

        cooked_data = BeautifulSoup(r.text, 'html.parser')
        td_text = cooked_data.find_all('td', {'class': 'cell-s'})
        mixed_list = [td.text for td in td_text]

        if len(mixed_list) >= 5:
            return {
                "soc_ver": soc_ver,
                "CPU": mixed_list[0],
                "GPU": mixed_list[1],
                "Mem": mixed_list[2],
                "UX": mixed_list[3],
                "Total": mixed_list[4]
            }
        else:
            return "Không tìm thấy đủ thông tin."
    except Exception as e:
        return f"Lỗi: {str(e)}"

def compare_results(results):
    # Sắp xếp danh sách kết quả theo điểm GPU từ cao đến thấp
    results_sorted = sorted(results, key=lambda x: float(x["GPU"]), reverse=True)

    max_values = {
        "CPU": max(results, key=lambda x: float(x["CPU"]))["CPU"],
        "GPU": max(results, key=lambda x: float(x["GPU"]))["GPU"],
        "Mem": max(results, key=lambda x: float(x["Mem"]))["Mem"],
        "UX": max(results, key=lambda x: float(x["UX"]))["UX"],
        "Total": max(results, key=lambda x: float(x["Total"]))["Total"]
    }

    for result in results_sorted:
        tree.insert("", "end", values=(
            result['soc_ver'],
            ("✔ " if result['CPU'] == max_values['CPU'] else "") + result['CPU'],
            ("✔ " if result['GPU'] == max_values['GPU'] else "") + result['GPU'],
            ("✔ " if result['Mem'] == max_values['Mem'] else "") + result['Mem'],
            ("✔ " if result['UX'] == max_values['UX'] else "") + result['UX'],
            ("✔ " if result['Total'] == max_values['Total'] else "") + result['Total']
        ))

def main():
    for i in tree.get_children():
        tree.delete(i)  # Xóa các kết quả cũ

    results = []

    n = int(entry_num.get())

    for i in range(n):
        value = entry_choice[i].get()
        soc_ver = entry_soc_ver[i].get().strip()

        # Chuyển đổi chuỗi: thay dấu cách bằng dấu '-' và chuyển thành chữ thường
        formatted_soc_ver = soc_ver.replace(' +', '-plus').replace('888', '875').replace('+', '-plus').replace(' ', '-').lower()

        if value == "Dimensity":
            url0 = "https://nanoreview.net/en/soc/mediatek-dimensity-"
        elif value == "Exynos":
            url0 = "https://nanoreview.net/en/soc/samsung-exynos-"
        elif value == "Snapdragon":
            url0 = "https://nanoreview.net/en/soc/qualcomm-snapdragon-"
        elif value == "Apple":
            url0 = "https://nanoreview.net/en/soc/apple-"
        elif value == "Unisoc":
            url0 = "https://nanoreview.net/en/soc/unisoc-"
        elif value == "Unisoc Tiger":
            url0 = "https://nanoreview.net/en/soc/unisoc-tiger-"
        elif value == "Tensor":
            url0 = "https://nanoreview.net/en/soc/google-tensor-"
        elif value == "Kirin":
            url0 = "https://nanoreview.net/en/soc/hisilicon-kirin-"
        elif value == "Helio":
            url0 = "https://nanoreview.net/en/soc/mediatek-helio-"
        else:
            tree.insert("", "end", values=("Tùy chọn không hợp lệ.", "", "", "", "", ""))
            return

        url = url0 + formatted_soc_ver  # Sử dụng chuỗi đã được định dạng
        result = info_finder(url, formatted_soc_ver)
        if isinstance(result, dict):
            results.append(result)
        else:
            tree.insert("", "end", values=(result, "", "", "", "", ""))

    compare_results(results)

def add_fields():
    n = int(entry_num.get())
    for i in range(n):
        Label(left_frame, text=f"Mời nhập tên của SoC thứ {i+1}:").grid(row=2+i*3, column=0, sticky='w', padx=5, pady=5)
        choice_var = StringVar(left_frame)
        choice_var.set("Snapdragon")  # Default value
        entry_choice.append(choice_var)
        OptionMenu(left_frame, choice_var, "Dimensity", "Exynos", "Snapdragon", "Apple", "Unisoc", "Unisoc Tiger", "Tensor", "Kirin", "Helio").grid(row=2+i*3, column=1, padx=5, pady=5)
        entry_soc_ver.append(Entry(left_frame))
        entry_soc_ver[-1].grid(row=3+i*3, column=1, padx=5, pady=5)

    # Show the "Nhập lại" and "Tra cứu" buttons at the bottom of the results table
    reset_button.grid(row=1, column=0, padx=5, pady=5, sticky='e')
    search_button.grid(row=1, column=1, padx=5, pady=5, sticky='e')

def reset_fields():
    # Xóa tất cả các hàng trong treeview (kết quả tra cứu cũ)
    for i in tree.get_children():
        tree.delete(i)

    # Xóa các trường nhập liệu và lựa chọn SoC hiện tại
    for widget in left_frame.winfo_children():
        widget.grid_forget()  # Ẩn tất cả các widget trong left_frame

    # Hiện lại trường nhập số lượng SoC và nút "Xác nhận"
    Label(left_frame, text="Bạn cần tra cứu bao nhiêu SoC?").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    entry_num.grid(row=0, column=1, padx=5, pady=5)
    confirm_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Ẩn nút "Nhập lại" và "Tra cứu"
    reset_button.grid_forget()
    search_button.grid_forget()

    # Xóa danh sách lựa chọn SoC và phiên bản SoC để chuẩn bị cho lần nhập mới
    entry_choice.clear()
    entry_soc_ver.clear()

# Initialize Tkinter
root = Tk()
root.title("Tra cứu điểm Antutu của SoC di động và so sánh")

# Left column
left_frame = ttk.Frame(root)
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

Label(left_frame, text="Bạn cần tra cứu bao nhiêu SoC?").grid(row=0, column=0, sticky='w', padx=5, pady=5)
entry_num = Entry(left_frame)
entry_num.grid(row=0, column=1, padx=5, pady=5)

confirm_button = Button(left_frame, text="Xác nhận", command=add_fields)
confirm_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# Initialize global variables
entry_choice = []
entry_soc_ver = []

# Right column
right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

tree = ttk.Treeview(right_frame, columns=("SoC", "CPU", "GPU", "Mem", "UX", "Total"), show='headings')
tree.heading("SoC", text="SoC")
tree.heading("CPU", text="CPU")
tree.heading("GPU", text="GPU")
tree.heading("Mem", text="Mem")
tree.heading("UX", text="UX")
tree.heading("Total", text="Total")

# Set column widths and make columns resizable
tree.column("SoC", width=150, stretch=True)
tree.column("CPU", width=100, stretch=True)
tree.column("GPU", width=100, stretch=True)
tree.column("Mem", width=100, stretch=True)
tree.column("UX", width=100, stretch=True)
tree.column("Total", width=100, stretch=True)

tree.grid(row=0, column=0, columnspan=2, sticky='nsew')

# Place buttons below the Treeview
reset_button = Button(right_frame, text="Nhập lại toàn bộ", command=reset_fields)
search_button = Button(right_frame, text="Tra cứu", command=main, bg='red', fg='white')

# Use grid to place buttons below the Treeview
reset_button.grid(row=1, column=0, padx=5, pady=5, sticky='e')
search_button.grid(row=1, column=1, padx=5, pady=5, sticky='e')

# Make the columns and rows resizable
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_columnconfigure(1, weight=1)

# Make the left_frame resizable
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(1, weight=1)

root.mainloop()
