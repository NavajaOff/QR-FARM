export const capitalizarPalabras = (texto = '') => {
  return texto
    .split(' ')
    .filter(Boolean)
    .map((fragmento) => {
      const minusculas = fragmento.toLowerCase();
      return `${minusculas.charAt(0).toUpperCase()}${minusculas.slice(1)}`;
    })
    .join(' ')
    .trim();
};

