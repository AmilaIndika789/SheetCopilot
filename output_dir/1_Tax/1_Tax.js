$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    
    // Define ranges for calculations
    const salesRange = sheet.getRange("B2:B11");
    const expensesRange = sheet.getRange("C2:C11");
    const profitRange = sheet.getRange("D2:D11");
    const taxRange = sheet.getRange("E2:E11");
    
    // Calculate Profit Before Tax
    profitRange.formulas = salesRange.formulas.map((row, index) => {
      return [row[0] - expensesRange.values[index][0]];
    });

    // Calculate Tax Expense
    taxRange.formulas = profitRange.formulas.map((row) => {
      return [row[0] * 0.225];
    });

    // Format the results with Accounting Number Format
    profitRange.numberFormat = [['"$"#,##0.00']];
    taxRange.numberFormat = [['"$"#,##0.00']];
    
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