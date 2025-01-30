function validatePhoneNumber(phoneNumber) {
      const phoneRegex = /^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/;
      return phoneRegex.test(phoneNumber);
  }

  // Export the function if using modules
  export { validatePhoneNumber };
