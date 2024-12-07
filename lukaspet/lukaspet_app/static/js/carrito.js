document.addEventListener("DOMContentLoaded", function () {
  function formatToCLP(number) {
    return "$" + number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function updateCartTotals(data) {
    document.getElementById("cart-count").textContent = data.cart_count;
    document.getElementById("cart-subtotal").textContent = formatToCLP(
      data.cart_total
    );
    document.getElementById("cart-total").textContent = formatToCLP(
      data.cart_total
    );
  }

  function showMessage(message, isError = false) {
    const toast = document.getElementById("notification-toast");
    const toastBody = toast.querySelector(".toast-body");
    toastBody.textContent = message;

    toast.classList.remove("bg-danger", "bg-success", "text-white");

    if (isError) {
      toast.classList.add("bg-danger", "text-white");
    } else {
      toast.classList.add("bg-success", "text-white");
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
  }

  document.querySelectorAll(".increase-quantity").forEach((button) => {
    button.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      const input = document.querySelector(`input[data-item-id="${itemId}"]`);
      const currentValue = parseInt(input.value);
      const maxValue = parseInt(input.max);

      if (currentValue < maxValue) {
        input.value = currentValue + 1;
        updateItemQuantity(itemId, currentValue + 1);
      } else {
        showMessage("No hay suficiente stock disponible", true);
      }
    });
  });

  document.querySelectorAll(".decrease-quantity").forEach((button) => {
    button.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      const input = document.querySelector(`input[data-item-id="${itemId}"]`);
      const currentValue = parseInt(input.value);

      if (currentValue > 1) {
        input.value = currentValue - 1;
        updateItemQuantity(itemId, currentValue - 1);
      }
    });
  });

  document.querySelectorAll(".item-quantity").forEach((input) => {
    input.addEventListener("change", function () {
      const itemId = this.dataset.itemId;
      let newValue = parseInt(this.value);
      const maxValue = parseInt(this.max);

      if (isNaN(newValue) || newValue < 1) {
        newValue = 1;
        this.value = 1;
      } else if (newValue > maxValue) {
        newValue = maxValue;
        this.value = maxValue;
        showMessage("No hay suficiente stock disponible", true);
      }

      updateItemQuantity(itemId, newValue);
    });
  });

  function updateItemQuantity(itemId, quantity) {
    const formData = new FormData();
    formData.append("item_id", itemId);
    formData.append("cantidad", quantity);
    formData.append(
      "csrfmiddlewaretoken",
      document.querySelector("[name=csrfmiddlewaretoken]").value
    );

    fetch("/carrito/actualizar/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          showMessage(data.error, true);
          return;
        }

        const subtotalElement = document.querySelector(
          `#item-${itemId} .item-subtotal`
        );
        if (subtotalElement) {
          subtotalElement.textContent = data.item_subtotal;
        }

        updateCartTotals(data);
        showMessage(data.message);
      })
      .catch((error) => {
        showMessage("Error al actualizar la cantidad", true);
      });
  }

  document.querySelectorAll(".remove-item").forEach((button) => {
    button.addEventListener("click", function () {
      const itemId = this.dataset.itemId;

      if (confirm("¿Estás seguro de que deseas eliminar este producto?")) {
        fetch(`/carrito/eliminar/${itemId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
              .value,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.error) {
              showMessage(data.error, true);
              return;
            }

            const itemRow = document.querySelector(`#item-${itemId}`);
            if (itemRow) {
              itemRow.remove();
            }

            updateCartTotals(data);
            showMessage(data.message);

            if (data.cart_count === 0) {
              location.reload();
            }
          })
          .catch((error) => {
            showMessage("Error al eliminar el producto", true);
          });
      }
    });
  });

  document
    .getElementById("vaciar-carrito")
    .addEventListener("click", function () {
      if (confirm("¿Estás seguro de que deseas vaciar el carrito?")) {
        fetch("/carrito/vaciar/", {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
              .value,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.error) {
              showMessage(data.error, true);
              return;
            }

            location.reload(); // Recargar la página para mostrar el carrito vacío
          })
          .catch((error) => {
            showMessage("Error al vaciar el carrito", true);
          });
      }
    });
});
