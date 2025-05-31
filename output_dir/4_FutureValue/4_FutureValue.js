$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange("A2:E5"); // Adjust range as needed
    range.load("values");

    await context.sync();

    const futureValues = range.values.map(row => {
      const presentValue = row[1];
      const years = row[2];
      const annualInterestRate = row[3];
      const compoundPeriods = row[4];
      return presentValue * Math.pow((1 + annualInterestRate / compoundPeriods), (years * compoundPeriods));
    });

    const futureValueRange = sheet.getRange("F2:F5"); // Future Value column
    futureValueRange.values = futureValues.map(value => [value]);

    await context.sync();
  });
}

/** Default helper for invoking an action and handling errors. */
async function tryCatch(callback) {
  try {
    await callback();
  } catch (error) {
    // Note: In a production add-in, you'd want to notify the user through your add-in's UI.
    console.error(error);
  }
}