import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/logIn.vue'
import TeacherHome from '../views/teacher/teacherHome.vue'
import StudentHome from '../views/student/studentHome.vue'

const routes = [
  {
    path: '/',
    redirect: '/logIn'
  },
  {
    path: '/logIn',
    name: 'logIn',
    component: Login
  },
  // 教师相关路由
  {
    path: '/teacher',
    redirect: '/teacher/home',
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/home',
    name: 'teacherHome',
    component: TeacherHome,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  /* 暂时注释掉尚未创建的教师页面
  {
    path: '/teacher/class',
    name: 'teacherClass',
    component: () => import('../views/teacher/TeacherClass.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/schedule',
    name: 'teacherSchedule',
    component: () => import('../views/teacher/TeacherSchedule.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/grades',
    name: 'teacherGrades',
    component: () => import('../views/teacher/TeacherGrades.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/analysis',
    name: 'teacherAnalysis',
    component: () => import('../views/teacher/TeacherAnalysis.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/answer',
    name: 'teacherAnswer',
    component: () => import('../views/teacher/TeacherAnswer.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/python',
    name: 'teacherPython',
    component: () => import('../views/teacher/TeacherPython.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  */
  
  // 学生相关路由
  {
    path: '/student',
    redirect: '/student/home',
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/home',
    name: 'studentHome',
    component: StudentHome,
    meta: { requiresAuth: true, role: 'student' }
  },
  /* 暂时注释掉尚未创建的学生页面
  {
    path: '/student/exams',
    name: 'studentExams',
    component: () => import('../views/student/StudentExams.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/homework',
    name: 'studentHomework',
    component: () => import('../views/student/StudentHomework.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/grades',
    name: 'studentGrades',
    component: () => import('../views/student/StudentGrades.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/question',
    name: 'studentQuestion',
    component: () => import('../views/student/StudentQuestion.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/aiChat',
    name: 'studentAiChat',
    component: () => import('../views/student/StudentAiChat.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  */
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'notFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 导航守卫，检查用户是否有权限访问页面
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录
    const userRole = localStorage.getItem('userRole')
    const username = localStorage.getItem('username')
    
    if (!userRole || !username) {
      // 未登录，跳转到登录页
      next({ 
        path: '/logIn',
        query: { redirect: to.fullPath } // 存储尝试访问的页面，以便登录后跳转
      })
    } else if (to.meta.role && to.meta.role !== userRole) {
      // 如果用户没有该页面的权限，重定向到对应主页
      next({ path: `/${userRole}/home` })
    } else {
      next() // 继续访问
    }
  } else {
    next() // 不需要权限的页面，直接访问
  }
})

export default router