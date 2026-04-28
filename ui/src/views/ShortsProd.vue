<script setup lang="ts"></script>

<template>
  <div class="card w-full max-w-2xl bg-base-100 shadow-xl mx-auto mt-4">
    <div class="card-body">
      <h2 class="card-title mb-4">Configuración</h2>

      <form class="space-y-4">
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text font-semibold">URL</span>
          </label>
          <input
            type="url"
            placeholder="https://ejemplo.com/video"
            class="input input-bordered w-full"
            required
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Start Segment (HH:MM:SS)</span>
            </label>
            <input
              type="text"
              pattern="^([0-9]{2}:){2}[0-9]{2}$"
              placeholder="00:00:00"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">End Segment (HH:MM:SS)</span>
            </label>
            <input
              type="text"
              pattern="^([0-9]{2}:){2}[0-9]{2}$"
              placeholder="00:00:00"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Hook Text</span>
            </label>
            <input
              type="text"
              placeholder="Escribe el hook aquí"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Outname</span>
            </label>
            <input
              type="text"
              placeholder="nombre_archivo"
              class="input input-bordered w-full"
              required
            />
          </div>
        </div>

        <div class="flex flex-col md:flex-row gap-6 pt-4">
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-3">
              <input type="checkbox" class="toggle toggle-primary" />
              <span class="label-text">Force Download</span>
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-3">
              <input type="checkbox" class="toggle toggle-primary" />
              <span class="label-text">Debug Video Frame</span>
            </label>
          </div>
        </div>

        <div class="card-actions justify-end mt-6">
          <button type="submit" class="btn btn-primary w-full md:w-auto">Enviar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped></style>
