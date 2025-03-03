import './assets/styles/globalTable.scss'
import './assets/main.css'

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from '@/utils/router'



const app = createApp(App)
// hello
app.use(router)
app.use(ElementPlus)
app.mount('#app')
