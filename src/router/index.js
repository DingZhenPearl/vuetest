import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/logIn.vue'
import TeacherHome from '../views/teacher/teacherHome.vue'
import StudentHome from '../views/student/studentHome.vue'
import StudentAiChat from '../views/student/StudentAiChat.vue' // 导入新组件
import StudentQuestion from '../views/student/StudentQuestion.vue'
import StudentProfile from '../views/student/StudentProfile.vue' // 导入个人信息组件
import StudentExams from '../views/student/StudentExams.vue' // 导入新组件
import StudentLearningAnalysis from '../views/student/StudentLearningAnalysis.vue' // 导入学习分析组件
import StudentProgrammingConcepts from '../views/student/StudentProgrammingConcepts.vue' // 导入编程概念组件

// 导入新组件
const TeacherProblems = () => import('../views/teacher/TeacherProblems.vue');
const TeacherDataAnalysis = () => import('../views/teacher/TeacherDataAnalysis.vue'); // 合并的数据分析组件
const TeacherTeachingContents = () => import('../views/teacher/TeacherTeachingContents.vue'); // 教学内容管理
const TeacherStudentDetail = () => import('../views/teacher/TeacherStudentDetail.vue'); // 学生详情页面
import TeacherProfile from '../views/teacher/TeacherProfile.vue'; // 教师个人信息页面

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
    path: '/teacher/problems',
    name: 'teacherProblems',
    component: TeacherProblems,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/data-analysis',
    name: 'teacherDataAnalysis',
    component: TeacherDataAnalysis,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/teaching-contents',
    name: 'teacherTeachingContents',
    component: TeacherTeachingContents,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/student-detail',
    name: 'teacherStudentDetail',
    component: TeacherStudentDetail,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/profile',
    name: 'teacherProfile',
    component: TeacherProfile,
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
  {
    path: '/student/exams',
    name: 'studentExams',
    component: StudentExams,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/learning-analysis',
    name: 'studentLearningAnalysis',
    component: StudentLearningAnalysis,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/programming-concepts',
    name: 'studentProgrammingConcepts',
    component: StudentProgrammingConcepts,
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

// 导航守卫，检查用户是否有权限访问页面并确保保留角色参数
router.beforeEach((to, from, next) => {
  // 优先检查URL中的角色参数
  const urlRole = to.query.role
  const userRole = sessionStorage.getItem('userRole') // 改为 sessionStorage
  const username = sessionStorage.getItem('username') // 改为 sessionStorage
  const userIdentifier = sessionStorage.getItem('userIdentifier') // 改为 sessionStorage

  // 确保所有页面跳转都携带角色参数和用户标识符
  const effectiveRole = urlRole || userRole

  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 如果没有登录凭证，跳转到登录页
    if (!username) {
      next({
        path: '/logIn',
        query: {
          redirect: to.fullPath,
          role: effectiveRole
        }
      })
      return
    }

    // 检查页面所需权限与有效角色是否匹配
    if (to.meta.role && to.meta.role !== effectiveRole) {
      // 角色不匹配，重定向到对应主页
      next({
        path: `/${effectiveRole}/home`,
        query: { role: effectiveRole, uid: userIdentifier }
      })
    } else {
      // 确保保留角色参数和用户标识符
      if ((effectiveRole && (!to.query.role || to.query.role !== effectiveRole)) ||
          (userIdentifier && (!to.query.uid || to.query.uid !== userIdentifier))) {
        next({
          path: to.path,
          query: { ...to.query, role: effectiveRole, uid: userIdentifier }
        })
      } else {
        next() // 继续访问
      }
    }
  } else {
    // 对于不需要权限的页面，也需要保留角色参数和用户标识符
    if ((effectiveRole && (!to.query.role || to.query.role !== effectiveRole)) ||
        (userIdentifier && (!to.query.uid || to.query.uid !== userIdentifier))) {
      next({
        path: to.path,
        query: { ...to.query, role: effectiveRole, uid: userIdentifier }
      })
    } else {
      next() // 直接访问
    }
  }
})

export default router