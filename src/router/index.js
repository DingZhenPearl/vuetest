import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/logIn.vue'
import StudentHome from '../views/student/studentHome.vue'
import TeacherHome from '../views/teacher/teacherHome.vue'

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
  {
    path: '/student',
    name: 'studentHome',
    component: StudentHome,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/teacher',
    name: 'teacherHome',
    component: TeacherHome,
    meta: { requiresAuth: true, role: 'teacher' }
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
    
    if (!userRole) {
      next({ name: 'logIn' }) // 修改为 logIn 而不是 Login
    } else if (to.meta.role && to.meta.role !== userRole) {
      // 如果用户没有该页面的权限
      next({ name: userRole === 'teacher' ? 'teacherHome' : 'studentHome' }) // 修改为实际名称
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router