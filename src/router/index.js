import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/LogIn.vue'
import TeacherHome from '../views/teacher/teacherHome.vue'
import StudentHome from '../views/student/studentHome.vue'
import StudentAiChat from '../views/student/StudentAiChat.vue' // 导入新组件
import StudentQuestion from '../views/student/StudentQuestion.vue'
import StudentProfile from '../views/student/StudentProfile.vue' // 导入个人信息组件

const routes = [
  {
    path: '/',
    redirect: '/LogIn'
  },
  {
    path: '/LogIn',
    name: 'LogIn',
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
  */
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
  {
    path: '/student/aiChat',
    name: 'studentAiChat',
    component: StudentAiChat,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/question',
    name: 'studentQuestion',
    component: StudentQuestion,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/profile',
    name: 'studentProfile',
    component: StudentProfile,
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
    // 优先检查URL中的角色参数
    const urlRole = to.query.role
    const userRole = localStorage.getItem('userRole')
    const username = localStorage.getItem('username')
    
    // 如果没有登录凭证，跳转到登录页
    if (!username) {
      next({ 
        path: '/logIn',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 确定本次访问使用的角色
    const effectiveRole = urlRole || userRole
    
    // 检查页面所需权限与有效角色是否匹配
    if (to.meta.role && to.meta.role !== effectiveRole) {
      // 角色不匹配，重定向到对应主页
      if (urlRole) {
        // 如果URL中有角色参数，使用该角色的主页，并保留角色参数
        next({ 
          path: `/${urlRole}/home`,
          query: { role: urlRole } 
        })
      } else {
        // 否则使用localStorage中的角色
        next({ path: `/${userRole}/home` })
      }
    } else {
      // 确保在next时保留角色参数
      if (urlRole && !to.query.role) {
        next({
          path: to.path,
          query: { ...to.query, role: urlRole }
        })
      } else {
        next() // 继续访问
      }
    }
  } else {
    // 对于不需要权限的页面，保留角色参数
    const urlRole = to.query.role
    if (urlRole && !to.query.role) {
      next({
        path: to.path,
        query: { ...to.query, role: urlRole }
      })
    } else {
      next() // 直接访问
    }
  }
})

export default router