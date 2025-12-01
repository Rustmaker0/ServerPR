import { createRouter, createWebHistory } from 'vue-router';
import PublicTransportsView from '../views/PublicTransportsView.vue';
import TransportsView from '../views/TransportsView.vue';
import MeasuringsView from '../views/MeasuringsView.vue';
import IntensivitysView from '../views/IntensivitysView.vue';
import PeoplesInPublicsTransportView from '../views/PeoplesInPublicsTransportView.vue';

import RegistrationView from '../views/RegistrationView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "MeasuringsView",
      component: MeasuringsView
    },
    {
      path: "/Intensivitys",
      name: "IntensivitysView",
      component: IntensivitysView
    },
    {
      path: "/PeoplesInPublicsTransportView",
      name: "PeoplesInPublicsTransportView",
      component: PeoplesInPublicsTransportView
    },
    {
      path: "/PublicTransports",
      name: "PublicTransportsView",
      component: PublicTransportsView
    },
    {
      path: "/Transports",
      name: "TransportsView",
      component: TransportsView
    },
    {
      path: "/register",
      name: "RegistrationView",
      component: RegistrationView
    }
  ]
})

export default router
