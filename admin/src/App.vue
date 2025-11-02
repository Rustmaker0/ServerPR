<template>
  <div class="container">
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavDropdown">
          <ul class="navbar-nav"> 
            <li class="nav-item">
              <router-link class="nav-link" to="/" active-class="active-link"><h1>Измерения</h1></router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/Transports" active-class="active-link">Транспорт</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/PublicTransports" active-class="active-link">Общественный транспорт</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/PublicTransportsNumbers" active-class="active-link">Номера общественного транспорта</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register" active-class="active-link">Администрирование</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
  <div class="container">
    <router-view />
  </div>
</template>

<style scoped>
.active-link {
  font-weight: bold; /* Выделение жирным шрифтом */
  text-decoration: underline; /* Добавление подчеркивания (по желанию) */
}

h1 {
  font-size: 1.5rem; /* Увеличение размера шрифта заголовка */
  margin: 0px 0; /* Отступ сверху и снизу */
  text-align: center; /* Центрирование заголовка */
}
</style>
