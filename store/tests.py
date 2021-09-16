from django.test import TestCase

# Create your tests here.

m_list = [2, 4, 6, 8, 7, 5, 50, 75, 92, 105, 30, 35, 30]

output = [8, 105, 35]

out = []
for i in range(len(m_list)):
    try:
        if m_list[i] > m_list[i + 1] and m_list[i] > m_list[i - 1]:
            out.append(m_list[i])
    except Exception:
        continue

print(out)
