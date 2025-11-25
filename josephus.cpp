/*
 * 约瑟夫环问题 (Josephus Problem)
 * 
 * 算法思想：
 * 1. 使用单向循环链表存储N个人的信息，每个节点包含编号和密码
 * 2. 从第一个人开始，按顺时针方向依次报数
 * 3. 报到M时，该人出列，将其密码作为新的M值
 * 4. 从出列者的下一个人继续报数
 * 5. 重复步骤3-4，直到所有人都出列
 * 
 * 数据结构：
 * - 使用单向循环链表，不需要头结点
 * - 每个节点包含：编号(id)、密码(password)、指向下一节点的指针(next)
 */

#include <iostream>
using namespace std;

// 定义链表节点结构
struct Node {
    int id;         // 编号
    int password;   // 密码
    Node* next;     // 指向下一个节点
};

// 创建循环链表
Node* createCircularList(int n, int passwords[]) {
    if (n <= 0) return nullptr;  // 空表处理
    
    Node* head = nullptr;
    Node* tail = nullptr;
    
    for (int i = 0; i < n; i++) {
        Node* newNode = new Node;
        newNode->id = i + 1;            // 编号从1开始
        newNode->password = passwords[i];
        newNode->next = nullptr;
        
        if (head == nullptr) {
            head = newNode;
            tail = newNode;
        } else {
            tail->next = newNode;
            tail = newNode;
        }
    }
    
    // 形成循环，尾节点指向头节点
    if (tail != nullptr) {
        tail->next = head;
    }
    
    return head;
}

// 约瑟夫环求解
void josephus(int n, int m, int passwords[]) {
    if (n <= 0) {
        cout << "人数必须大于0！" << endl;
        return;
    }
    
    // 创建循环链表
    Node* head = createCircularList(n, passwords);
    if (head == nullptr) return;
    
    Node* current = head;
    Node* prev = nullptr;
    
    // 找到尾节点（作为初始的prev）
    Node* temp = head;
    while (temp->next != head) {
        temp = temp->next;
    }
    prev = temp;
    
    cout << "出列顺序为：";
    
    int count = n;
    bool first = true;
    
    while (count > 0) {
        // 报数m-1次（因为当前节点算第1个）
        for (int i = 1; i < m; i++) {
            prev = current;
            current = current->next;
        }
        
        // 输出当前出列者的编号
        if (!first) {
            cout << "，";
        }
        cout << current->id;
        first = false;
        
        // 保存密码作为新的M值
        m = current->password;
        
        // 删除当前节点
        Node* toDelete = current;
        prev->next = current->next;
        current = current->next;
        
        delete toDelete;
        count--;
    }
    
    cout << endl;
}

int main() {
    int n, m;
    
    cout << "========== 约瑟夫环问题求解 ==========" << endl;
    cout << endl;
    
    cout << "请输入初始报数上限值M：";
    cin >> m;
    
    cout << "请输入总人数N（N<=30）：";
    cin >> n;
    
    if (n <= 0 || n > 30) {
        cout << "人数必须在1到30之间！" << endl;
        return 1;
    }
    
    if (m <= 0) {
        cout << "报数上限值必须为正整数！" << endl;
        return 1;
    }
    
    int* passwords = new int[n];
    
    cout << "请依次输入" << n << "个人的密码（正整数）：" << endl;
    for (int i = 0; i < n; i++) {
        cout << "第" << (i + 1) << "个人的密码：";
        cin >> passwords[i];
        if (passwords[i] <= 0) {
            cout << "密码必须为正整数！" << endl;
            delete[] passwords;
            return 1;
        }
    }
    
    cout << endl;
    josephus(n, m, passwords);
    
    delete[] passwords;
    
    return 0;
}
