import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'

import ContinueButton from './components/ContinueButton.vue'
import MasteryChecklist from './components/MasteryChecklist.vue'
import ProgressPill from './components/ProgressPill.vue'
import GitHubIssues from './components/GitHubIssues.vue'
import RecentlyUpdated from './components/RecentlyUpdated.vue'
import MasteryDashboard from './components/MasteryDashboard.vue'
import GitHubBoard from './components/GitHubBoard.vue'
import LessonsIndex from './components/LessonsIndex.vue'

const theme: Theme = {
  ...DefaultTheme,
  enhanceApp({ app, router }) {
    app.component('ContinueButton', ContinueButton)
    app.component('MasteryChecklist', MasteryChecklist)
    app.component('ProgressPill', ProgressPill)
    app.component('GitHubIssues', GitHubIssues)
    app.component('RecentlyUpdated', RecentlyUpdated)
    app.component('MasteryDashboard', MasteryDashboard)
    app.component('GitHubBoard', GitHubBoard)
    app.component('LessonsIndex', LessonsIndex)

    // "Press / to focus search" UX
    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', (e: KeyboardEvent) => {
        const tag = (e.target as HTMLElement)?.tagName?.toLowerCase()
        const typing = tag === 'input' || tag === 'textarea' || (e as any).isComposing
        if (e.key === '/' && !typing) {
          e.preventDefault()
          const input = document.querySelector('input[type="search"]') as HTMLInputElement | null
          if (input) {
            input.focus()
            input.select()
          }
        }
      })
    }

    // Track last visited lesson for "Continue" button
    router.onAfterRouteChanged = (to) => {
      try {
        if (to?.startsWith('/lessons/')) {
          localStorage.setItem('lastVisitedLesson', to)
          localStorage.setItem('lastMasterclassLesson', to)
        }
      } catch (_) {
        // ignore if storage not available
      }
    }
  }
}

export default theme

