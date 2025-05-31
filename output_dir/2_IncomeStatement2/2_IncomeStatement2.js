$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    
    // Add a new column header for "Sales Tax"
    sheet.getRange("K1").values = [["Sales Tax"]];
    
    // Calculate Sales Tax in the new column
    const salesRange = sheet.getRange("B2:B10");
    const salesTaxFormula = `=B2*0.2`; // 20% tax rate
    const salesTaxRange = sheet.getRange("K2:K10");
    salesTaxRange.formulas = [[salesTaxFormula], [salesTaxFormula], [salesTaxFormula], [salesTaxFormula], [salesTaxFormula], [salesTaxFormula], [salesTaxFormula], [salesTaxFormula], [salesTaxFormula]];

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