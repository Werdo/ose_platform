/**
 * Vue Router Configuration
 * This is a placeholder for shared router configuration
 * Each app will have its own router instance
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

export interface RouterOptions {
  routes: RouteRecordRaw[]
  baseUrl?: string
}

export function createAppRouter(options: RouterOptions) {
  const router = createRouter({
    history: createWebHistory(options.baseUrl),
    routes: options.routes,
    scrollBehavior(_to, _from, savedPosition) {
      if (savedPosition) {
        return savedPosition
      } else {
        return { top: 0 }
      }
    },
  })

  return router
}

export { type RouteRecordRaw }
