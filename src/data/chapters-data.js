// 章节数据
const chaptersData = [
  {
    id: 'ch1',
    number: '第一章',
    title: '绪论',
    difficulty: '入门',
    description: '本章介绍数据结构的基本概念、算法分析方法以及时间复杂度和空间复杂度的基础知识。',
    sections: [
      {
        id: 'ch1-s1',
        title: '数据结构概述',
        type: 'theory',
        duration: 15,
        content: '<p>数据结构是计算机存储、组织数据的方式。数据结构是指相互之间存在一种或多种特定关系的数据元素的集合。</p><p>本节将介绍数据结构的基本概念和分类。</p>',
        examples: [
          {
            title: '数据结构的分类',
            code: '线性结构：数组、链表、栈、队列\n非线性结构：树、图、堆\n文件结构：顺序文件、索引文件、散列文件',
            explanation: '这是数据结构的基本分类，不同的数据结构适用于不同的应用场景。'
          }
        ]
      },
      {
        id: 'ch1-s2',
        title: '算法分析基础',
        type: 'theory',
        duration: 20,
        content: '<p>算法分析是指对一个算法所需的计算资源进行预测和度量。主要包括时间复杂度和空间复杂度的分析。</p>',
        examples: [
          {
            title: '常见的时间复杂度',
            code: 'O(1)    - 常数时间复杂度\nO(log n) - 对数时间复杂度\nO(n)    - 线性时间复杂度\nO(n log n) - 线性对数时间复杂度\nO(n²)   - 平方时间复杂度\nO(n³)   - 立方时间复杂度\nO(2ⁿ)   - 指数时间复杂度',
            explanation: '时间复杂度表示算法执行时间与数据规模之间的关系，O表示渐进上界。'
          }
        ]
      },
      {
        id: 'ch1-s3',
        title: '算法效率分析',
        type: 'exercise',
        duration: 25,
        content: '<p>算法效率分析是评估算法性能的重要手段，通过分析算法的时间复杂度和空间复杂度来比较不同算法的优劣。</p>',
        task: '分析以下代码片段的时间复杂度，并解释你的分析过程。',
        template: '// 代码片段1\nfor (int i = 0; i < n; i++) {\n    sum += i;\n}\n\n// 代码片段2\nfor (int i = 0; i < n; i++) {\n    for (int j = 0; j < n; j++) {\n        sum += i * j;\n    }\n}'
      },
      {
        id: 'ch1-s4',
        title: '数据结构基本认知与必要知识复习',
        type: 'video',
        duration: 30,
        videoUrl: '//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=1&high_quality=1&danmaku=0&as_wide=1',
        content: '<p>本视频介绍了数据结构的基本概念和必要的预备知识，帮助你建立对数据结构的基本认知。</p><p>视频来源：<a href="https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383" target="_blank">数据结构与算法入门</a></p>'
      },
      {
        id: 'ch1-s5',
        title: '指针_结构体_动态内存分配_算法时间复杂度',
        type: 'video',
        duration: 30,
        videoUrl: '//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=2&high_quality=1&danmaku=0&as_wide=1',
        content: '<p>本视频介绍了数据结构实现所需的C++基础知识，包括指针、结构体、动态内存分配，以及算法时间复杂度的概念。</p><p>视频来源：<a href="https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383&p=2" target="_blank">数据结构与算法入门</a></p>'
      },
      {
        id: 'ch1-s6',
        title: '绪论知识测验',
        type: 'quiz',
        duration: 10,
        content: '<p>完成以下测验来测试你对数据结构绪论的理解。</p>',
        questions: [
          {
            text: '以下哪种时间复杂度最高效？',
            options: ['O(n²)', 'O(n log n)', 'O(n)', 'O(log n)'],
            correctAnswer: 3
          },
          {
            text: '数据结构主要研究的内容是什么？',
            options: ['数据的逻辑结构', '数据的物理结构', '数据的操作', '以上都是'],
            correctAnswer: 3
          },
          {
            text: '以下哪种不是线性数据结构？',
            options: ['数组', '链表', '树', '栈'],
            correctAnswer: 2
          }
        ]
      }
    ]
  },
  {
    id: 'ch2',
    number: '第二章',
    title: '线性表',
    difficulty: '基础',
    description: '本章介绍线性表的基本概念、顺序存储结构和链式存储结构，以及线性表的基本操作实现。',
    sections: [
      {
        id: 'ch2-s1',
        title: '线性表的基本概念',
        type: 'theory',
        duration: 20,
        content: '<p>线性表是具有相同数据类型的n个数据元素的有限序列。线性表中元素之间是一对一的关系。</p>',
        examples: [
          {
            title: '线性表的抽象数据类型',
            code: 'ADT 线性表(List)\n数据对象：D = {a₁, a₂, ..., aₙ | aᵢ ∈ ElemSet, i = 1, 2, ..., n, n ≥ 0}\n数据关系：R = {<a₁, a₂>, <a₂, a₃>, ..., <aₙ₋₁, aₙ>}\n基本操作：\n  InitList(&L)       // 初始化线性表\n  Length(L)          // 返回线性表长度\n  GetElem(L, i, &e)  // 获取第i个元素\n  LocateElem(L, e)   // 查找元素e的位置\n  ListInsert(&L, i, e) // 在位置i插入元素e\n  ListDelete(&L, i, &e) // 删除位置i的元素',
            explanation: '线性表的抽象数据类型定义了线性表的数据对象、数据关系和基本操作。'
          }
        ]
      },
      {
        id: 'ch2-s2',
        title: '顺序表与链表',
        type: 'video',
        duration: 30,
        videoUrl: '//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=3&high_quality=1&danmaku=0&as_wide=1',
        content: '<p>本视频详细介绍了线性表的两种主要实现方式：顺序表和链表，包括它们的基本结构、实现原理和操作方法。</p><p>视频来源：<a href="https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383&p=3" target="_blank">数据结构与算法入门</a></p>'
      },
      {
        id: 'ch2-s3',
        title: '链表应用_循环链表',
        type: 'video',
        duration: 30,
        videoUrl: '//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=4&high_quality=1&danmaku=0&as_wide=1',
        content: '<p>本视频介绍了链表的实际应用场景和循环链表的概念、实现方法及其特点。</p><p>视频来源：<a href="https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383&p=4" target="_blank">数据结构与算法入门</a></p>'
      }
    ]
  },
  {
    id: 'ch3',
    number: '第三章',
    title: '线性表的扩展',
    difficulty: '中级',
    description: '本章介绍栈、队列、串等线性表的扩展结构，以及它们的基本操作和应用。',
    sections: [
      {
        id: 'ch3-s1',
        title: '栈的基本概念与实现',
        type: 'theory',
        duration: 25,
        content: '<p>栈是一种特殊的线性表，它只允许在一端进行插入和删除操作。栈遵循后进先出(LIFO)原则。</p>',
        examples: [
          {
            title: '栈的顺序存储实现',
            code: 'typedef struct {\n    ElemType *base;  // 栈底指针\n    ElemType *top;   // 栈顶指针\n    int stacksize;   // 栈的大小\n} SqStack;\n\n// 初始化栈\nStatus InitStack(SqStack &S) {\n    S.base = new ElemType[MAXSIZE];\n    if (!S.base) return ERROR;\n    S.top = S.base;\n    S.stacksize = MAXSIZE;\n    return OK;\n}\n\n// 入栈操作\nStatus Push(SqStack &S, ElemType e) {\n    if (S.top - S.base == S.stacksize) return ERROR;\n    *S.top++ = e;\n    return OK;\n}\n\n// 出栈操作\nStatus Pop(SqStack &S, ElemType &e) {\n    if (S.top == S.base) return ERROR;\n    e = *--S.top;\n    return OK;\n}',
            explanation: '这个例子展示了栈的顺序存储实现，包括栈的初始化、入栈和出栈操作。'
          }
        ]
      },
      {
        id: 'ch3-s2',
        title: '双向链表_栈_队列',
        type: 'video',
        duration: 30,
        videoUrl: '//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=5&high_quality=1&danmaku=0&as_wide=1',
        content: '<p>本视频介绍了双向链表的结构和实现，以及栈和队列这两种重要的线性表扩展结构的概念、特性和基本操作。</p><p>视频来源：<a href="https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383&p=5" target="_blank">数据结构与算法入门</a></p>'
      },
      {
        id: 'ch3-s3',
        title: '循环队列_讲题_递归',
        type: 'video',
        duration: 30,
        videoUrl: '//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=6&high_quality=1&danmaku=0&as_wide=1',
        content: '<p>本视频介绍了循环队列的概念和实现方法，并通过实例讲解了递归的基本原理和应用。</p><p>视频来源：<a href="https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383&p=6" target="_blank">数据结构与算法入门</a></p>'
      }
    ]
  },
  {
    id: 'ch4',
    number: '第四章',
    title: '树',
    difficulty: '中级',
    description: '本章介绍树的基本概念、二叉树的性质和存储结构，以及树的遍历算法和应用。',
    sections: [
      {
        id: 'ch4-s1',
        title: '树的基本概念',
        type: 'theory',
        duration: 20,
        content: '<p>树是n个结点的有限集合。当n=0时，称为空树；当n>0时，树有一个特定的结点称为根结点，其余结点可分为m个互不相交的有限集，每个集合本身又是一棵树。</p>',
        examples: [
          {
            title: '树的术语',
            code: '结点：树中的每个元素\n根结点：树的顶层结点，没有父结点\n父结点：有子结点的结点\n子结点：有父结点的结点\n兄弟结点：具有相同父结点的结点\n叶结点：没有子结点的结点\n结点的度：结点的子树个数\n树的度：树中结点的最大度数\n层次：根结点在第1层，其子结点在第2层，以此类推\n树的高度：树中结点的最大层次',
            explanation: '这些是描述树结构的基本术语，理解这些概念对学习树结构非常重要。'
          }
        ]
      }
    ]
  },
  {
    id: 'ch5',
    number: '第五章',
    title: '图',
    difficulty: '高级',
    description: '本章介绍图的基本概念、存储结构、遍历算法以及最短路径、最小生成树等经典图算法。',
    sections: [
      {
        id: 'ch5-s1',
        title: '图的基本概念',
        type: 'theory',
        duration: 25,
        content: '<p>图是由顶点集合和边集合组成的。图中的顶点可以通过边相连，表示它们之间的关系。</p>',
        examples: [
          {
            title: '图的分类',
            code: '有向图：边有方向\n无向图：边没有方向\n完全图：任意两个顶点之间都有边\n连通图：任意两个顶点之间都存在路径\n带权图：边上带有权值',
            explanation: '图可以根据边的方向、顶点的连接情况和边的权值等特征进行分类。'
          }
        ]
      }
    ]
  },
  {
    id: 'ch6',
    number: '第六章',
    title: '查找',
    difficulty: '中级',
    description: '本章介绍各种查找算法，包括顺序查找、二分查找、哈希查找等，以及它们的性能分析和应用场景。',
    sections: [
      {
        id: 'ch6-s1',
        title: '查找的基本概念',
        type: 'theory',
        duration: 15,
        content: '<p>查找是在数据集合中寻找特定元素的过程。查找算法的效率直接影响程序的性能。</p>',
        examples: [
          {
            title: '顺序查找算法',
            code: 'int SequentialSearch(int arr[], int n, int key) {\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == key) {\n            return i;  // 找到元素，返回位置\n        }\n    }\n    return -1;  // 未找到元素\n}',
            explanation: '顺序查找是最简单的查找算法，它按顺序检查每个元素，直到找到目标元素或检查完所有元素。'
          }
        ]
      }
    ]
  },
  {
    id: 'ch7',
    number: '第七章',
    title: '排序',
    difficulty: '中级',
    description: '本章介绍各种排序算法，包括冒泡排序、插入排序、快速排序、归并排序等，以及它们的性能分析和应用场景。',
    sections: [
      {
        id: 'ch7-s1',
        title: '排序的基本概念',
        type: 'theory',
        duration: 20,
        content: '<p>排序是将一组数据按照特定顺序重新排列的过程。排序算法的效率对于处理大量数据非常重要。</p>',
        examples: [
          {
            title: '冒泡排序算法',
            code: 'void BubbleSort(int arr[], int n) {\n    for (int i = 0; i < n-1; i++) {\n        for (int j = 0; j < n-i-1; j++) {\n            if (arr[j] > arr[j+1]) {\n                // 交换元素\n                int temp = arr[j];\n                arr[j] = arr[j+1];\n                arr[j+1] = temp;\n            }\n        }\n    }\n}',
            explanation: '冒泡排序是一种简单的排序算法，它重复地遍历要排序的数列，一次比较两个元素，如果它们的顺序错误就交换它们。'
          }
        ]
      }
    ]
  }
];

module.exports = chaptersData;
